"""批量修复所有 Vue 文件中的 AI 风格样式"""
import re, os, glob

VIEWS = glob.glob(r"c:\Source\SQL监控平台\frontend\src\views\*.vue")
COMPONENTS = glob.glob(r"c:\Source\SQL监控平台\frontend\src\components\*.vue")
FILES = VIEWS + COMPONENTS

# 替换规则: (pattern, replacement)
RULES = [
    # border-radius: 10px -> 6px
    (r'border-radius:\s*10px', 'border-radius: 6px'),
    # border-radius: 12px -> 6px
    (r'border-radius:\s*12px', 'border-radius: 6px'),
    # border-radius: 16px -> 8px (login card)
    (r'border-radius:\s*16px', 'border-radius: 8px'),
    # border-radius: 22px -> 11px (switch/toggle)
    (r'border-radius:\s*22px', 'border-radius: 11px'),
    # linear-gradient buttons -> solid color
    (r'background:\s*linear-gradient\(135deg,\s*#1890ff,\s*#096dd9\)', 'background: #1890ff'),
    (r'background:\s*linear-gradient\(135deg,\s*#2563eb\s*0%,\s*#1d4ed8\s*100%\)', 'background: #1d4ed8'),
    (r'background:\s*linear-gradient\(135deg,\s*#3b82f6\s*0%,\s*#2563eb\s*100%\)', 'background: #2563eb'),
    (r'background:\s*linear-gradient\(135deg,\s*#52c41a,\s*#389e0d\)', 'background: #52c41a'),
    (r'background:\s*linear-gradient\(135deg,\s*#4f46e5,\s*#6366f1\)', 'background: #4f46e5'),
    (r'background:\s*linear-gradient\(135deg,\s*#4338ca,\s*#4f46e5\)', 'background: #4338ca'),
    (r'background:\s*linear-gradient\(135deg,\s*#722ed1,\s*#531dab\)', 'background: #722ed1'),
    # linear-gradient backgrounds -> solid
    (r'background:\s*linear-gradient\(135deg,\s*#f0f4ff\s*0%,\s*#faf5ff\s*100%\)', 'background: #f7f8fa'),
    (r'background:\s*linear-gradient\(180deg,\s*#fafbff,\s*#fafafa\)', 'background: #fafafa'),
    (r'background:\s*linear-gradient\(180deg,\s*#1890ff,\s*#52c41a\)', 'background: #1890ff'),
    (r'background:\s*linear-gradient\(90deg,\s*#1890ff,\s*#52c41a\)', 'background: #1890ff'),
    (r'background:\s*linear-gradient\(135deg,\s*#1890ff,\s*#096dd9\)', 'background: #1890ff'),
    (r'background:\s*linear-gradient\(135deg,\s*rgba\(24,\s*144,\s*255,\s*0\.1\),\s*rgba\(82,\s*196,\s*26,\s*0\.1\)\)', 'background: #f7f8fa'),
    # box-shadow: 0 8px 24px -> 0 2px 8px
    (r'box-shadow:\s*0\s+8px\s+24px', 'box-shadow: 0 2px 8px'),
    # transform: translateY(-2px) -> remove
    (r'transform:\s*translateY\(-2px\);\s*', ''),
    # transition: all 0.3s -> all 0.2s
    (r'transition:\s*all\s+0\.3s', 'transition: all 0.2s'),
    # stat-card remove icon backgrounds
    (r'\.stat-icon\s*\{[^}]*\}', '.stat-icon { display: none; }'),
]

changed_files = []
for filepath in FILES:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original = content
    for pattern, replacement in RULES:
        content = re.sub(pattern, replacement, content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        changed_files.append(os.path.basename(filepath))
        print(f"Fixed: {os.path.basename(filepath)}")

print(f"\nTotal: {len(changed_files)} files modified")
print("Files:", ", ".join(changed_files))
