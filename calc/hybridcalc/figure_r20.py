"""Dependency-free scientific SVG plot generated from the decode table."""
import html
import math


def batching_svg(rows):
    keys=('b300_fp8','b300_fp8_kv','pro6000_fp8')
    colors=('#1565c0','#00897b','#c62828');parts=['<svg xmlns="http://www.w3.org/2000/svg" width="880" height="510" viewBox="0 0 880 510">',
        '<rect width="880" height="510" fill="white"/>',
        '<g font-family="sans-serif" fill="#222">',
        '<text x="70" y="30" font-size="19">Server decode batching gain (modelled; requested batch 32)</text>',
        '<text x="70" y="52" font-size="12">Weights read once per batch; each session reads its KV. Batch is limited by VRAM.</text>']
    x=lambda d:80+650*(math.log(d)-math.log(16000))/(math.log(1000000)-math.log(16000))
    y=lambda gain:390-310*(gain-1)/19
    for gain in (1,5,10,15,20):
        parts.append(f'<path d="M80 {y(gain):.3f} H730" stroke="#ddd"/><text x="40" y="{y(gain)+4:.3f}">{gain}×</text>')
    for depth,label in ((16000,'16k'),(64000,'64k'),(164000,'164k'),(1000000,'1M')):
        parts.append(f'<path d="M{x(depth):.3f} 80 V390" stroke="#eee"/><text x="{x(depth)-13:.3f}" y="415">{label}</text>')
    for index,(key,color)in enumerate(zip(keys,colors)):
        samples=sorted((r for r in rows if r['server']==key and r['requested_streams']==32 and isinstance(r['gain'],(int,float))),key=lambda r:r['depth'])
        pts=' '.join(f"{x(r['depth']):.3f},{y(r['gain']):.3f}"for r in samples)
        parts.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="2.5"/>')
        for r in samples:
            parts.append(f'<circle cx="{x(r["depth"]):.3f}" cy="{y(r["gain"]):.3f}" r="4" fill="{color}"/><text x="{x(r["depth"])+5:.3f}" y="{y(r["gain"])-7:.3f}" font-size="11">{r["gain"]:.2f}×; B={r["batch"]}</text>')
        parts.append(f'<text x="{80+index*225}" y="455" fill="{color}" font-size="13">{html.escape(key)}</text>')
    parts.extend(['<text x="650" y="370" fill="#c62828" font-size="11">PRO 1M: does not fit</text>',
        '<text x="290" y="435" font-size="13">Context depth (log scale)</text>',
        '<text x="70" y="487" font-size="12">1M is an architecture/bandwidth extrapolation, not a measured vLLM context claim.</text></g></svg>'])
    return '\n'.join(parts)+'\n'
