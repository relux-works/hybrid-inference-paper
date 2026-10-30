import Foundation
import Testing

private let unit = URL(fileURLWithPath: #filePath).deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent().deletingLastPathComponent()
private let script = ProcessInfo.processInfo.environment["SESSION_STATS_TEST_SCRIPT"] ?? unit.appendingPathComponent("agent_session_stats.py").path

private func process(_ argv: [String]) throws -> (Int32, String) {
    let p = Process(); p.executableURL = URL(fileURLWithPath: "/usr/bin/env"); p.arguments = argv
    let pipe = Pipe(); p.standardOutput = pipe; p.standardError = pipe
    try p.run(); let data = pipe.fileHandleForReading.readDataToEndOfFile(); p.waitUntilExit()
    return (p.terminationStatus, String(decoding: data, as: UTF8.self))
}
private func directory() throws -> URL {
    let p = unit.deletingLastPathComponent().appendingPathComponent(".temp/session-stats-tests/fixtures/\(UUID().uuidString)")
    try FileManager.default.createDirectory(at: p, withIntermediateDirectories: true)
    return p
}
private func json(_ value: Any, _ path: URL) throws {
    try FileManager.default.createDirectory(at: path.deletingLastPathComponent(), withIntermediateDirectories: true)
    try JSONSerialization.data(withJSONObject: value, options: [.sortedKeys]).write(to: path)
}
private func log(_ records: [[String: Any]], _ path: URL, tail: String = "") throws {
    try FileManager.default.createDirectory(at: path.deletingLastPathComponent(), withIntermediateDirectories: true)
    var data = Data()
    for row in records { data.append(try JSONSerialization.data(withJSONObject: row, options: [.sortedKeys])); data.append(10) }
    data.append(contentsOf: tail.utf8); try data.write(to: path)
}
private func run(_ root: URL, roots: [String:[String]], zip: [String] = [], extra: [String] = []) throws -> ([String:Any], Int32, String) {
    let manifest = root.appendingPathComponent("sources.json"), out = root.appendingPathComponent("out.json")
    try json(["roots": roots, "zip_roots":zip], manifest)
    let result = try process(["python3", "-I", "-S", "-B", script, "--sources", manifest.path, "--out",out.path,"--coverage",root.appendingPathComponent("coverage.json").path,"--csv",root.appendingPathComponent("calls.csv").path] + extra)
    let report = try #require(JSONSerialization.jsonObject(with: Data(contentsOf: out)) as? [String:Any])
    return (report, result.0, result.1)
}
private func stats(_ report: [String:Any], _ agent: String) throws -> [String:Any] {
    try #require((report["agents"] as? [String:[String:Any]])?[agent])
}
private func claude(_ id: String, _ output: Int, input: Int = 2, cache: Int = 7, write: Int = 11) -> [String:Any] {
    ["type":"assistant","sessionId":"PRIVATE-SESSION-CANARY","timestamp":"2026-01-01T00:00:00Z", "message":["id":id,"model":"claude-test","usage":["input_tokens":input,"cache_read_input_tokens":cache,"cache_creation_input_tokens":write,"output_tokens":output],"content":[["type":"text","text":"PRIVATE-CONTENT-CANARY"]]]]
}
private func cu(_ input: Int, _ output: Int) -> [String:Int] {
    ["input_tokens":input,"cached_input_tokens":0,"output_tokens":output,"reasoning_output_tokens":0,"total_tokens":input+output]
}
private func legacy(_ u: [String:Int], _ total: Int) -> [String:Any] {
    ["type":"event_msg","timestamp":"2026-01-01T00:00:01Z","payload":["type":"token_count","info":["last_token_usage":u,"total_token_usage":["total_tokens":total]]]]
}

@Suite(.serialized)
struct SessionStatsTests {
    // Partial blocks, a backup copy, and a one-call context are retained exactly once with final numeric usage.
    @Test func claudeCopiesAndShortSessions() throws {
        let r = try directory(), projects = r.appendingPathComponent("projects")
        let rows = [claude("msg-1",1,input:0,cache:0,write:0),claude("msg-1",5),claude("msg-2",9)]
        try log(rows, projects.appendingPathComponent("one.jsonl"))
        try log(rows, projects.appendingPathComponent("backup.jsonl"))
        try log([claude("msg-2",9),claude("msg-3",2)], projects.appendingPathComponent("divergent.jsonl"))
        let (report, exit, _) = try run(r, roots:["claude":[projects.path]])
        let s = try stats(report,"claude"), totals = try #require(s["totals"] as? [String:Int]), cov = try #require(s["coverage"] as? [String:Int])
        #expect(exit == 0); #expect(s["calls"] as? Int == 3); #expect(totals["prompt"] == 60); #expect(totals["output"] == 16)
        #expect(cov["duplicate_content_files"] == 1); #expect((cov["duplicate_call_records"] ?? 0) >= 2)
    }
    // Migrated Codex retains pre-migration calls while removing only matching modern/legacy updates, even with added fields.
    @Test func codexMixedFormats() throws {
        let r = try directory(), sessions = r.appendingPathComponent("sessions")
        let older = cu(100,10), newer = cu(200,20)
        var modernUsage = newer; modernUsage["cache_write_input_tokens"] = 0
        let rows: [[String:Any]] = [
            ["type":"session_meta","payload":["id":"PRIVATE-CODEX-CANARY"]],
            ["type":"turn_context","payload":["model":"codex-test"]],
            legacy(older,110),legacy(older,110),
            ["type":"token_usage_record","timestamp":"2026-01-01T00:00:02Z","payload":["thread_id":"PRIVATE-CODEX-CANARY","response_id":"response-new","usage":modernUsage,"thread_token_usage":["total_tokens":330,"cache_write_input_tokens":0]]],
            legacy(newer,330)
        ]
        try log(rows, sessions.appendingPathComponent("rollout-a.jsonl"))
        let (report, exit, _) = try run(r, roots:["codex":[sessions.path]])
        let s = try stats(report,"codex"), cov = try #require(s["coverage"] as? [String:Int])
        #expect(exit == 0); #expect(s["calls"] as? Int == 2)
        #expect((s["totals"] as? [String:Int])?["prompt"] == 300)
        #expect(cov["legacy_updates_matched_to_modern"] == 1); #expect(cov["repeated_legacy_updates"] == 1)
    }
    // Muse framed and projected copies share source identity; cache counts never trigger the previous input-addition heuristic.
    @Test func museFramesAndCacheAccounting() throws {
        let r = try directory(), sessions = r.appendingPathComponent("sessions")
        var event: [String:Any] = ["record_type":"event","payload_type":"runtime.session","id":"projection-a","stream":["session":"PRIVATE-MUSE-CANARY"],"recorded_at":"2026-01-01T00:00:00Z","payload":["source_run_record_id":"original-call","event":["kind":"model_completed","model":"muse-test","usage":["input_tokens":10,"cached_tokens":100,"output_tokens":4,"reasoning_tokens":2]]]]
        let encoded = String(decoding:try JSONSerialization.data(withJSONObject:event),as:UTF8.self)
        try log([["children":[["record_json":encoded]]]], sessions.appendingPathComponent("one/session.jsonl"))
        event["id"] = "projection-b"; try log([event], sessions.appendingPathComponent("two/session.jsonl"))
        let (report, exit, _) = try run(r, roots:["muse":[sessions.path]])
        let s = try stats(report,"muse")
        #expect(exit == 0); #expect(s["calls"] as? Int == 1)
        #expect((s["totals"] as? [String:Int])?["prompt"] == 10)
        #expect((s["totals"] as? [String:Int])?["cached"] == 100)
    }
    // A call present only in ZIP is included, duplicate members are removed, and extraction cannot write the embedded traversal path.
    @Test func archiveOnlyCoverage() throws {
        let r = try directory(), z = r.appendingPathComponent("archives")
        try FileManager.default.createDirectory(at:z,withIntermediateDirectories:true)
        let file = r.appendingPathComponent("projects/one.jsonl"); try log([claude("msg-zip",3)],file)
        let code = "import zipfile,sys; p=sys.argv; z=zipfile.ZipFile(p[1],'w'); z.write(p[2],'cumulative/claude/projects/one.jsonl'); z.write(p[2],'versions/old/claude/projects/copy.jsonl'); z.writestr('../../escape','CANARY'); z.close()"
        let made = try process(["python3","-I","-S","-B","-c",code,z.appendingPathComponent("backup.zip").path,file.path]); #expect(made.0 == 0)
        try FileManager.default.removeItem(at:file)
        let (report, exit, _) = try run(r, roots:[:],zip:[z.path]); let s = try stats(report,"claude")
        #expect(exit == 0); #expect(s["calls"] as? Int == 1)
        #expect((s["coverage"] as? [String:Int])?["duplicate_content_files"] == 1)
        #expect(!FileManager.default.fileExists(atPath:r.appendingPathComponent("escape").path))
    }
    // Invalid JSON/counts and corrupt archives are explicit partial results; valid neighbors survive without leaking conversation/native IDs.
    @Test func malformedAndPrivacy() throws {
        let r = try directory(), projects = r.appendingPathComponent("projects"), zip = r.appendingPathComponent("archives")
        try log([claude("good",7),claude("bad",-1)], projects.appendingPathComponent("one.jsonl"),tail:"{bad-json\n[]\n")
        try FileManager.default.createDirectory(at:zip,withIntermediateDirectories:true)
        try Data("invalid".utf8).write(to:zip.appendingPathComponent("bad.zip"))
        let (report, exit, stdout) = try run(r, roots:["claude":[projects.path]],zip:[zip.path])
        let s = try stats(report,"claude"), cov = try #require(s["coverage"] as? [String:Int])
        #expect(exit == 2); #expect(report["status"] as? String == "partial"); #expect(s["calls"] as? Int == 1)
        #expect(cov["invalid_usage_records"] == 1); #expect(cov["invalid_json_rows"] == 1); #expect(cov["non_object_rows"] == 1)
        for name in ["out.json","coverage.json","calls.csv"] {
            let output = try String(contentsOf:r.appendingPathComponent(name),encoding:.utf8)
            #expect(!output.contains("PRIVATE-CONTENT-CANARY")); #expect(!output.contains("PRIVATE-SESSION-CANARY"))
        }
        #expect(!stdout.contains("CANARY"))
    }
    // An empty corpus and user-requested truncation cannot report complete; archived_sessions work through explicit Codex roots.
    @Test func emptyAndFilters() throws {
        let r = try directory(); let (empty, exit, _) = try run(r, roots:[:])
        #expect(exit == 2); #expect(empty["status"] as? String == "partial")
        let sessions = r.appendingPathComponent("archived_sessions")
        let row: [String:Any] = ["type":"token_usage_record","payload":["response_id":"archived-only","usage":cu(123,4)]]
        try log([row],sessions.appendingPathComponent("rollout-archive.jsonl"))
        let (report, good, _) = try run(r, roots:["codex":[sessions.path]])
        #expect(good == 0); #expect(try stats(report,"codex")["calls"] as? Int == 1)
        let (filtered, bad, _) = try run(r, roots:["codex":[sessions.path]],extra:["--max-mb","0.000001"])
        #expect(bad == 2); #expect(filtered["status"] as? String == "partial")
        #expect(try stats(filtered,"codex")["coverage"] as? [String:Int] == ["files_discovered":1,"bytes_discovered":try Data(contentsOf:sessions.appendingPathComponent("rollout-archive.jsonl")).count,"files_size_filtered":1])
    }
}

@Suite(.serialized)
struct CrossFileCodexTests {
    // Matching cumulative counters join a legacy backup to the same modern response regardless of discovery order.
    @Test func crossFileModernLegacyIdentity() throws {
        for modernFirst in [true,false] {
            let r = try directory(), sessions = r.appendingPathComponent("sessions")
            let sid = "PRIVATE-CROSS-FORMAT-CANARY", u = cu(100,10), total = u
            var old: [[String:Any]] = [["type":"session_meta","payload":["id":sid]],legacy(u,110)]
            var current: [[String:Any]] = [["type":"session_meta","payload":["id":sid]],
              ["type":"token_usage_record","payload":["thread_id":sid,"response_id":"stable-response","usage":u,"thread_token_usage":total]]]
            // Use the same full counter shape in both representations.
            old[1] = ["type":"event_msg","payload":["type":"token_count","info":["last_token_usage":u,"total_token_usage":total]]]
            if modernFirst { current.append(["type":"ignored","padding":String(repeating:"x",count:1000)]) }
            else { old.append(["type":"ignored","padding":String(repeating:"x",count:1000)]) }
            try log(old,sessions.appendingPathComponent("rollout-backup.jsonl"))
            try log(current,sessions.appendingPathComponent("rollout-live.jsonl"))
            let (report,exit,_) = try run(r,roots:["codex":[sessions.path]])
            let s = try stats(report,"codex")
            #expect(exit == 0); #expect(s["calls"] as? Int == 1)
            #expect((s["totals"] as? [String:Int])?["prompt"] == 100)
            #expect((s["coverage"] as? [String:Int])?["cross_format_identity_matches"] == 1)
        }
    }
}

@Suite(.serialized)
struct ArchiveEfficiencyTests {
    // Two unique archive members parse fully while the central directory opens only once for discovery and once for reading.
    @Test func oneIndexPerArchive() throws {
        let r = try directory(), z = r.appendingPathComponent("archives")
        try FileManager.default.createDirectory(at:z,withIntermediateDirectories:true)
        let a = r.appendingPathComponent("projects/a.jsonl"), b = r.appendingPathComponent("projects/b.jsonl")
        try log([claude("unique-a",2)],a); try log([claude("unique-b",3)],b)
        let make = "import zipfile,sys; z=zipfile.ZipFile(sys.argv[1],'w'); z.write(sys.argv[2],'cumulative/claude/projects/a.jsonl'); z.write(sys.argv[3],'cumulative/claude/projects/b.jsonl'); z.close()"
        #expect(try process(["python3","-I","-S","-B","-c",make,z.appendingPathComponent("sample.zip").path,a.path,b.path]).0 == 0)
        let manifest = r.appendingPathComponent("sources.json"), out = r.appendingPathComponent("out.json")
        try json(["roots":[:],"zip_roots":[z.path]],manifest)
        let wrapper = """
        import sys,zipfile,runpy
        real=zipfile.ZipFile
        count=0
        def opened(*a,**kw):
            global count
            count+=1
            return real(*a,**kw)
        zipfile.ZipFile=opened
        sys.argv=sys.argv[1:]
        try:runpy.run_path(sys.argv[0],run_name='__main__')
        except SystemExit as e:
            print('ZIP_OPEN_COUNT='+str(count))
            raise
        """
        let p = try process(["python3","-I","-S","-B","-c",wrapper,script,"--sources",manifest.path,"--out",out.path])
        #expect(p.0 == 0); #expect(p.1.contains("ZIP_OPEN_COUNT=2\n"))
        let report = try #require(JSONSerialization.jsonObject(with:Data(contentsOf:out)) as? [String:Any])
        #expect(try stats(report,"claude")["calls"] as? Int == 2)
        #expect((try stats(report,"claude")["totals"] as? [String:Int])?["output"] == 5)
    }
}

@Suite(.serialized)
struct ProfileDiscoveryTests {
    // Actual home-directory layout enumeration includes alternate Codex/Claude profiles without scanning real user data in this fixture.
    @Test func alternateHomes() throws {
        let r = try directory()
        for name in [".codex-base/sessions", ".codex-relux/sessions", ".claude-old/projects"] {
            try FileManager.default.createDirectory(at:r.appendingPathComponent(name),withIntermediateDirectories:true)
        }
        let code = """
        import sys,importlib.util,pathlib,json
        spec=importlib.util.spec_from_file_location('stats',sys.argv[1])
        m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
        fixture=pathlib.Path(sys.argv[2]);pathlib.Path.home=classmethod(lambda cls:fixture)
        print(json.dumps(m.default_roots()))
        """
        let result = try process(["python3","-I","-S","-B","-c",code,script,r.path])
        #expect(result.0 == 0)
        let d = try #require(JSONSerialization.jsonObject(with:Data(result.1.utf8)) as? [String:Any])
        let roots = try #require(d["roots"] as? [String:[String]])
        #expect(roots["codex"]?.contains(r.appendingPathComponent(".codex-base/sessions").path) == true)
        #expect(roots["codex"]?.contains(r.appendingPathComponent(".codex-relux/sessions").path) == true)
        #expect(roots["claude"]?.contains(r.appendingPathComponent(".claude-old/projects").path) == true)
    }
}

@Suite(.serialized)
struct ModelMetadataTests {
    // Malformed model labels never become dictionary keys or leak content; a later valid block restores the label for the same call.
    @Test func malformedModelLabel() throws {
        let r = try directory(), projects = r.appendingPathComponent("projects"), file = projects.appendingPathComponent("one.jsonl")
        var row = claude("model-label",2)
        var m = try #require(row["message"] as? [String:Any]); m["model"] = ["unexpected":"PRIVATE-METADATA-CANARY"]; row["message"] = m
        try log([row,row],file)
        let (report,exit,stdout) = try run(r,roots:["claude":[projects.path]])
        #expect(exit == 0); #expect(try stats(report,"claude")["calls"] as? Int == 1)
        #expect(try stats(report,"claude")["unknown_model_calls"] as? Int == 1)
        #expect(!stdout.contains("PRIVATE-METADATA-CANARY"))
        try log([row,row,claude("model-label",2)],file)
        let (valid,good,_) = try run(r,roots:["claude":[projects.path]])
        #expect(good == 0); #expect(try stats(valid,"claude")["unknown_model_calls"] as? Int == 0)
    }
}

private func at(_ id: String, _ timestamp: Any?) -> [String:Any] {
    var row = claude(id, 3); row["timestamp"] = timestamp; return row
}
private func times(_ report: [String:Any], _ agent: String) throws -> [String:Any] {
    try #require(try stats(report, agent)["call_time"] as? [String:Any])
}

@Suite(.serialized)
struct CallTimeTests {
    // Real reader timestamps normalize to UTC; gaps and provider overlap do not become extra distinct days.
    @Test func readersAndUTCUnion() throws {
        let r = try directory(), c = r.appendingPathComponent("projects"), x = r.appendingPathComponent("sessions"), m = r.appendingPathComponent("muse")
        try log([at("c1", "2026-01-02T00:30:00+02:00"), at("c2", "2026-01-10T01:00:00")], c.appendingPathComponent("one.jsonl"))
        try log([["type":"token_usage_record", "timestamp":"2026-01-01T22:30:00Z", "payload":["response_id":"x1", "usage":cu(4,2)]]], x.appendingPathComponent("rollout-one.jsonl"))
        try log([["payload_type":"runtime.session", "id":"m1", "recorded_at":"2026-01-10T01:00:00Z", "payload":["event":["kind":"model_completed", "usage":["input_tokens":5,"output_tokens":2]]]]], m.appendingPathComponent("one/session.jsonl"))
        let (report, exit, _) = try run(r, roots:["claude":[c.path], "codex":[x.path], "muse":[m.path]])
        let all = try times(report,"all"), ct = try times(report,"claude")
        #expect(exit == 0); #expect(all["first_utc"] as? String == "2026-01-01T22:30:00Z")
        #expect(all["last_utc"] as? String == "2026-01-10T01:00:00Z")
        #expect(all["distinct_utc_days"] as? Int == 2); #expect(ct["distinct_utc_days"] as? Int == 2)
        #expect(all["timestamped_calls"] as? Int == 4); #expect(all["status"] as? String == "complete")
        #expect(try times(report,"codex")["timestamped_calls"] as? Int == 1)
        #expect(try times(report,"muse")["timestamped_calls"] as? Int == 1)
    }
    // Identity updates fill missing/invalid dates, retain the first valid value, flag conflicts once, and ignore byte-identical copies.
    @Test func duplicateTimes() throws {
        let r = try directory(), p = r.appendingPathComponent("projects")
        let rows = [at("fill",nil), at("fill","bad"), at("fill","2026-02-01T00:00:00Z"), at("fill","2026-02-02T00:00:00Z"), at("fill","2026-02-03T00:00:00Z"), at("invalid","bad"), at("invalid",nil), at("numeric",1769904000000 as Int64), at("numeric","2026-02-01T00:00:00Z")]
        try log(rows,p.appendingPathComponent("one.jsonl")); try log(rows,p.appendingPathComponent("copy.jsonl"))
        let (report,exit,_) = try run(r,roots:["claude":[p.path]]); let t = try times(report,"claude")
        #expect(exit == 0); #expect(try stats(report,"claude")["calls"] as? Int == 3)
        #expect(t["timestamped_calls"] as? Int == 2); #expect(t["distinct_utc_days"] as? Int == 1)
        #expect(t["conflicting_timestamp_calls"] as? Int == 1); #expect(t["invalid_timestamp_calls"] as? Int == 1)
        #expect(t["missing_timestamp_calls"] as? Int == 0); #expect(t["status"] as? String == "partial")
        #expect(t["last_utc"] as? String == "2026-02-01T00:00:00Z")
    }
    // Supplied invalid dates keep their usage, valid neighbors survive, and file mtime cannot fill missing dates.
    @Test func invalidDatesAndNoMtime() throws {
        let r = try directory(), p = r.appendingPathComponent("projects"), f = p.appendingPathComponent("2026-09-01.jsonl")
        try log([at("missing",nil), at("bool",true), at("empty",""), at("range",1e30), at("bad","bad"), at("good", "2026-01-01T00:00:00Z")], f)
        // JSON's nonfinite extension is deliberately injected as raw source data, not through Foundation serialization.
        let h = try FileHandle(forWritingTo:f); try h.seekToEnd()
        for value in ["NaN","Infinity","-Infinity"] {
            var raw = at("nonfinite-"+value, "RAW-TIME")
            raw["timestamp"] = "RAW-TIME"
            var data = String(decoding:try JSONSerialization.data(withJSONObject:raw),as:UTF8.self)
            data = data.replacingOccurrences(of:"\"RAW-TIME\"",with:value)
            try h.write(contentsOf:Data((data+"\n").utf8))
        }; try h.close()
        try FileManager.default.setAttributes([.modificationDate:Date(timeIntervalSince1970:2_000_000_000)],ofItemAtPath:f.path)
        let (report,exit,_) = try run(r,roots:["claude":[p.path]]); let t = try times(report,"all")
        #expect(exit == 0); #expect(try stats(report,"all")["calls"] as? Int == 9)
        #expect(t["timestamped_calls"] as? Int == 1); #expect(t["missing_timestamp_calls"] as? Int == 1)
        #expect(t["invalid_timestamp_calls"] as? Int == 7); #expect(t["distinct_utc_days"] as? Int == 1)
        #expect(t["status"] as? String == "partial"); #expect(t["first_utc"] as? String == "2026-01-01T00:00:00Z")
    }
    // Empty and all-invalid corpora expose null boundaries; min-call filtering excludes short-context dates as well as tokens.
    @Test func emptyAndFilteredTimes() throws {
        let r = try directory(); let (empty,_,_) = try run(r,roots:[:]); let et = try times(empty,"all")
        #expect(et["status"] as? String == "no_calls"); #expect(et["first_utc"] is NSNull)
        #expect(et["last_utc"] is NSNull); #expect(et["distinct_utc_days"] as? Int == 0)
        let p = r.appendingPathComponent("projects")
        var short = at("short","2020-01-01T00:00:00Z"); short["sessionId"] = "short-context"
        try log([at("one",nil),at("two","bad"),short],p.appendingPathComponent("one.jsonl"))
        let (report,exit,_) = try run(r,roots:["claude":[p.path]],extra:["--min-calls","2"]); let t = try times(report,"all")
        #expect(exit == 2); #expect(try stats(report,"all")["calls"] as? Int == 2)
        #expect(t["status"] as? String == "no_timestamped_calls"); #expect(t["first_utc"] is NSNull)
        #expect(t["distinct_utc_days"] as? Int == 0); #expect(t["missing_timestamp_calls"] as? Int == 1)
        #expect(t["invalid_timestamp_calls"] as? Int == 1)
    }
    // Distinct valid conflicting times alone prevent complete time coverage, without inflating days.
    @Test func conflictOnlyAndRepeatedLegacy() throws {
        let r = try directory(), p = r.appendingPathComponent("sessions"), u = cu(100,10)
        var first = legacy(u,110); first.removeValue(forKey:"timestamp")
        var changed = legacy(u,110); changed["timestamp"] = "2026-02-01T00:00:00Z"
        try log([first,legacy(u,110),changed],p.appendingPathComponent("rollout-one.jsonl"))
        let (report,exit,_) = try run(r,roots:["codex":[p.path]]); let t = try times(report,"codex")
        #expect(exit == 0); #expect(try stats(report,"codex")["calls"] as? Int == 1)
        #expect(t["timestamped_calls"] as? Int == 1); #expect(t["distinct_utc_days"] as? Int == 1)
        #expect(t["conflicting_timestamp_calls"] as? Int == 1); #expect(t["status"] as? String == "partial")
        #expect(t["last_utc"] as? String == "2026-01-01T00:00:01Z")
    }
    // Suppressed modern/legacy duplicates can supply missing time without becoming extra calls or extra days.
    @Test func codexSuppressedTimeMetadata() throws {
        let r = try directory(), p = r.appendingPathComponent("sessions"), u = cu(100,10)
        let rows: [[String:Any]] = [["type":"session_meta","payload":["id":"time-context"]], ["type":"token_usage_record","payload":["thread_id":"time-context","response_id":"one","usage":u,"thread_token_usage":["total_tokens":110]]], legacy(u,110)]
        try log(rows,p.appendingPathComponent("rollout-one.jsonl"))
        let (report,exit,_) = try run(r,roots:["codex":[p.path]]); let t = try times(report,"codex")
        #expect(exit == 0); #expect(try stats(report,"codex")["calls"] as? Int == 1)
        #expect(t["timestamped_calls"] as? Int == 1); #expect(t["first_utc"] as? String == "2026-01-01T00:00:01Z")
    }
}

private func usageRows(_ report: [String:Any]) throws -> [[String:Any]] {
    try #require(report["model_usage"] as? [[String:Any]])
}
private func reconcileModels(_ report: [String:Any]) throws {
    let rows = try usageRows(report)
    for agent in ["claude", "codex", "muse", "all"] {
        let s = try stats(report, agent), totals = try #require(s["totals"] as? [String:Int])
        let selected = rows.filter { agent == "all" || $0["agent"] as? String == agent }
        #expect(try selected.reduce(0) { try $0 + #require($1["calls"] as? Int) } == s["calls"] as? Int)
        for key in ["prompt", "cached", "output", "reasoning"] {
            #expect(try selected.reduce(0) { try $0 + #require($1[key] as? Int) } == totals[key])
        }
    }
}
private func museUsage(_ id: String, _ model: String, _ usage: [String:Any]) -> [String:Any] {
    ["payload_type":"runtime.session", "id":id, "stream":["session":"raw-muse"],
     "payload":["event":["kind":"model_completed", "model":model, "usage":usage]]]
}

@Suite(.serialized)
struct ModelUsageTests {
    // Claude's measured 100/20/300 categories survive duplicate partials; their sum includes cache write and equals legacy prompt.
    @Test func claudeRawCategoriesReconcile() throws {
        let r = try directory(), p = r.appendingPathComponent("projects")
        var full = claude("raw-claude",9,input:100,cache:300,write:20)
        var message = try #require(full["message"] as? [String:Any])
        var u = try #require(message["usage"] as? [String:Any]); u["output_tokens_details"] = ["thinking_tokens":4]
        message["usage"] = u; full["message"] = message
        try log([claude("raw-claude",1,input:0,cache:0,write:0), full, full],p.appendingPathComponent("one.jsonl"))
        let (report,exit,_) = try run(r,roots:["claude":[p.path]])
        let rows = try usageRows(report), row = try #require(rows.first)
        #expect(exit == 0); #expect(report["version"] as? String == "1.6-model-usage"); #expect(rows.count == 1)
        #expect(row["uncached_input"] as? Int == 100); #expect(row["cache_write"] as? Int == 20)
        #expect(row["cache_read"] as? Int == 300); #expect(row["raw_input"] as? Int == 100)
        #expect(row["output"] as? Int == 9); #expect(row["raw_output"] as? Int == 9)
        #expect(row["reasoning"] as? Int == 4); #expect(row["raw_reasoning"] as? Int == 4)
        let parts = try ["uncached_input", "cache_write", "cache_read"].map { try #require(row[$0] as? Int) }
        #expect(parts.reduce(0,+) == row["prompt"] as? Int)
        #expect(row["prompt"] as? Int == 420); #expect(row["cached"] as? Int == 300)
        #expect(row["cache_write_5m"] is NSNull); #expect(row["cache_write_1h"] is NSNull)
        #expect(row["unknown_counters"] as? [String] == ["cache_write_5m", "cache_write_1h"])
        try reconcileModels(report)
    }

    // Codex reports inclusive input and measured cache read; reasoning stays separate and absent writes are unknown.
    @Test func codexMeasuredCacheRead() throws {
        let r = try directory(), p = r.appendingPathComponent("sessions")
        var u = cu(500,17); u["cached_input_tokens"] = 300; u["reasoning_output_tokens"] = 6
        let rows: [[String:Any]] = [["type":"session_meta", "payload":["id":"raw-codex"]],
          ["type":"turn_context", "payload":["model":"codex-raw"]],
          ["type":"token_usage_record", "payload":["response_id":"x-raw", "usage":u, "thread_token_usage":u]],
          ["type":"event_msg", "payload":["type":"token_count", "info":["last_token_usage":u,"total_token_usage":u]]]]
        try log(rows,p.appendingPathComponent("rollout-raw.jsonl"))
        let (report,exit,_) = try run(r,roots:["codex":[p.path]])
        let row = try #require(try usageRows(report).first)
        #expect(exit == 0); #expect(row["calls"] as? Int == 1)
        #expect(row["prompt"] as? Int == 500); #expect(row["uncached_input"] as? Int == 200)
        #expect(row["cached"] as? Int == 300); #expect(row["cache_read"] as? Int == 300)
        #expect(row["cache_write"] is NSNull); #expect(row["output"] as? Int == 17)
        #expect(row["reasoning"] as? Int == 6); #expect(row["raw_reasoning"] as? Int == 6)
        try reconcileModels(report)
    }

    // Muse missing cache stays null, measured zero stays zero, and a mixed group cannot claim a complete raw total.
    @Test func museUnknownVersusZero() throws {
        let r = try directory(), p = r.appendingPathComponent("muse")
        let rows = [museUsage("missing","missing",["input_tokens":10,"output_tokens":4]),
                    museUsage("zero","zero",["input_tokens":10,"output_tokens":4,"cached_tokens":0,"reasoning_tokens":0]),
                    museUsage("mixed-missing","mixed",["input_tokens":10,"output_tokens":4]),
                    museUsage("mixed-known","mixed",["input_tokens":10,"output_tokens":4,"cache_read_tokens":7])]
        try log(rows,p.appendingPathComponent("one/session.jsonl"))
        let (report,exit,_) = try run(r,roots:["muse":[p.path]])
        let usage = try usageRows(report)
        let missing = try #require(usage.first { $0["model"] as? String == "missing" })
        let zero = try #require(usage.first { $0["model"] as? String == "zero" })
        let mixed = try #require(usage.first { $0["model"] as? String == "mixed" })
        #expect(exit == 0); #expect(missing["cache_read"] is NSNull); #expect(zero["cache_read"] as? Int == 0)
        #expect(missing["raw_reasoning"] is NSNull); #expect(zero["raw_reasoning"] as? Int == 0)
        #expect(mixed["cache_read"] is NSNull); #expect(mixed["cached"] as? Int == 7)
        #expect((mixed["unknown_counter_calls"] as? [String:Int])?["cache_read"] == 1)
        for row in usage {
            #expect(row["cache_semantics"] as? String == "unverified")
            #expect(row["uncached_input"] is NSNull); #expect(row["cache_write"] is NSNull)
            #expect(row["raw_input"] as? Int == (row["model"] as? String == "mixed" ? 20 : 10))
        }
        try reconcileModels(report)
    }

    // Filtering uses deduplicated context size, retains null models, separates agents with equal model labels, and preserves unfiltered legacy models.
    @Test func filteredModelsAndUnknownReconcile() throws {
        let r = try directory(), c = r.appendingPathComponent("projects"), x = r.appendingPathComponent("sessions"), m = r.appendingPathComponent("muse")
        var unknown = claude("unknown",3), message = try #require(unknown["message"] as? [String:Any])
        message.removeValue(forKey:"model"); unknown["message"] = message
        var short = claude("short",999); short["sessionId"] = "short-context"
        try log([claude("known",4),unknown,unknown,short],c.appendingPathComponent("one.jsonl"))
        try log([["type":"turn_context","payload":["model":"claude-test"]],
                 ["type":"token_usage_record","payload":["response_id":"x1","usage":cu(50,5)]],
                 ["type":"token_usage_record","payload":["response_id":"x2","usage":cu(60,6)]]],x.appendingPathComponent("rollout-one.jsonl"))
        try log([museUsage("m1","short-muse",["input_tokens":9,"output_tokens":9])],m.appendingPathComponent("one/session.jsonl"))
        let (report,exit,_) = try run(r,roots:["claude":[c.path],"codex":[x.path],"muse":[m.path]],extra:["--min-calls","2"])
        let rows = try usageRows(report), unknownRow = try #require(rows.first { $0["model"] is NSNull })
        #expect(exit == 2); #expect(rows.count == 3); #expect(unknownRow["calls"] as? Int == 1)
        #expect(!rows.contains { $0["agent"] as? String == "muse" })
        #expect(rows.filter { $0["model"] as? String == "claude-test" }.count == 2)
        let legacyModels = try #require(report["models"] as? [[String:Any]])
        #expect(legacyModels.count == 3)
        #expect(legacyModels.first { $0["agent"] as? String == "claude" }?["calls"] as? Int == 2)
        try reconcileModels(report)
    }

    // Missing usage is excluded by all three readers; missing raw fields do not replace legacy zero defaults or invent TTLs.
    @Test func missingUsageAndTTLMeasurements() throws {
        let r = try directory(), c = r.appendingPathComponent("projects"), x = r.appendingPathComponent("sessions"), m = r.appendingPathComponent("muse")
        var invalid = claude("no-usage",999), im = try #require(invalid["message"] as? [String:Any])
        im.removeValue(forKey:"usage"); invalid["message"] = im
        var valid = claude("ttl",0,input:0,cache:0,write:20), vm = try #require(valid["message"] as? [String:Any])
        var u = try #require(vm["usage"] as? [String:Any]); u["cache_creation"] = ["ephemeral_5m_input_tokens":0,"ephemeral_1h_input_tokens":20]
        vm["usage"] = u; valid["message"] = vm
        try log([invalid,valid],c.appendingPathComponent("one.jsonl"))
        try log([["type":"token_usage_record","payload":["response_id":"bad"]],
                 ["type":"token_usage_record","payload":["response_id":"good","usage":["input_tokens":5,"output_tokens":0]]]],x.appendingPathComponent("rollout-one.jsonl"))
        var badMuse = museUsage("bad","bad",[:]); var payload = try #require(badMuse["payload"] as? [String:Any])
        payload["event"] = ["kind":"model_completed"]; badMuse["payload"] = payload
        try log([badMuse,museUsage("good","good",["input_tokens":0,"output_tokens":0])],m.appendingPathComponent("one/session.jsonl"))
        let (report,exit,_) = try run(r,roots:["claude":[c.path],"codex":[x.path],"muse":[m.path]])
        let rows = try usageRows(report), cr = try #require(rows.first { $0["agent"] as? String == "claude" })
        let xr = try #require(rows.first { $0["agent"] as? String == "codex" })
        #expect(exit == 2); #expect(rows.count == 3); #expect(try stats(report,"all")["calls"] as? Int == 3)
        #expect(cr["cache_write_5m"] as? Int == 0); #expect(cr["cache_write_1h"] as? Int == 20)
        #expect(cr["raw_output"] as? Int == 0); #expect(cr["raw_reasoning"] is NSNull)
        #expect(xr["cached"] as? Int == 0); #expect(xr["cache_read"] is NSNull); #expect(xr["uncached_input"] is NSNull)
        try reconcileModels(report)
        let (empty,emptyExit,_) = try run(try directory(),roots:[:])
        #expect(emptyExit == 2); #expect(try usageRows(empty).isEmpty); try reconcileModels(empty)
    }

    // Null required values keep prior zero-default acceptance; raw absence stays null, and impossible Codex subtraction stays unknown.
    @Test func nullRawValuesAndInvalidCacheDifference() throws {
        let r = try directory(), p = r.appendingPathComponent("sessions")
        try log([["type":"turn_context","payload":["model":"null-values"]],
                 ["type":"token_usage_record","payload":["response_id":"null","usage":["input_tokens":NSNull(),"output_tokens":NSNull()]]],
                 ["type":"turn_context","payload":["model":"invalid-difference"]],
                 ["type":"token_usage_record","payload":["response_id":"over","usage":["input_tokens":10,"output_tokens":0,"cached_input_tokens":11]]]],p.appendingPathComponent("rollout-one.jsonl"))
        let (report,exit,_) = try run(r,roots:["codex":[p.path]])
        let rows = try usageRows(report), missing = try #require(rows.first { $0["model"] as? String == "null-values" })
        let over = try #require(rows.first { $0["model"] as? String == "invalid-difference" })
        #expect(exit == 0); #expect(missing["raw_input"] is NSNull); #expect(missing["raw_output"] is NSNull)
        #expect(missing["prompt"] as? Int == 0); #expect(missing["output"] as? Int == 0)
        #expect(over["cache_read"] as? Int == 11); #expect(over["uncached_input"] is NSNull)
        try reconcileModels(report)
    }

    // A reported sum adds only the calls that report the counter: a mixed group keeps its measured part, an
    // all-missing group reports 0 with every call counted unknown, and wherever the strict total exists the two agree.
    @Test func reportedSumsCountOnlyReportingCalls() throws {
        let r = try directory(), p = r.appendingPathComponent("muse")
        let rows = [museUsage("missing","missing",["input_tokens":10,"output_tokens":4]),
                    museUsage("zero","zero",["input_tokens":10,"output_tokens":4,"cached_tokens":0,"reasoning_tokens":0]),
                    museUsage("mixed-missing","mixed",["input_tokens":10,"output_tokens":4]),
                    museUsage("mixed-known","mixed",["input_tokens":10,"output_tokens":4,"cache_read_tokens":7])]
        try log(rows,p.appendingPathComponent("one/session.jsonl"))
        let (report,exit,_) = try run(r,roots:["muse":[p.path]])
        let usage = try usageRows(report)
        let missing = try #require(usage.first { $0["model"] as? String == "missing" })
        let zero = try #require(usage.first { $0["model"] as? String == "zero" })
        let mixed = try #require(usage.first { $0["model"] as? String == "mixed" })
        #expect(exit == 0)
        #expect(mixed["cache_read"] is NSNull); #expect(mixed["cache_read_reported_sum"] as? Int == 7)
        #expect((mixed["unknown_counter_calls"] as? [String:Int])?["cache_read"] == 1)
        #expect(missing["cache_read"] is NSNull); #expect(missing["cache_read_reported_sum"] as? Int == 0)
        #expect((missing["unknown_counter_calls"] as? [String:Int])?["cache_read"] == 1)
        #expect(zero["cache_read"] as? Int == 0); #expect(zero["cache_read_reported_sum"] as? Int == 0)
        #expect((zero["unknown_counter_calls"] as? [String:Int])?["cache_read"] == nil)
        let counters = ["raw_input", "uncached_input", "cache_write", "cache_read", "raw_output", "raw_reasoning",
                        "cache_write_5m", "cache_write_1h"]
        for row in usage {
            for key in counters {
                #expect(row[key + "_reported_sum"] as? Int != nil)
                if let strict = row[key] as? Int { #expect(row[key + "_reported_sum"] as? Int == strict) }
            }
        }
    }
}
