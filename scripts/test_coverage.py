"""验证 references 文档里宣称的校验能力是否真的生效。"""
import subprocess, json, sys, os, tempfile

SCRIPT = r"D:\Hermes\workspace\2026-11-25-gads-copy-skill\scripts\validate_gads_copy.py"
BASE = r"D:\Hermes\workspace\2026-11-25-gads-copy-skill\examples\hiitio-example.json"

base = json.load(open(BASE, encoding='utf-8'))

def run(payload, extra_args=None):
    fd, path = tempfile.mkstemp(suffix='.json', text=True)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        json.dump(payload, f, ensure_ascii=False)
    cmd = [sys.executable, SCRIPT, path] + (extra_args or [])
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    os.unlink(path)
    return r.returncode, r.stdout

cases = [
    # (名称, 修改函数, 期望被捕获的关键词)
    ("合规基线", lambda p: None, None),
    ("标题超30", lambda p: p['groups'][0]['headlines'].__setitem__(0, "X"*31), "上限 30"),
    ("说明超90", lambda p: p['groups'][0]['descriptions'].__setitem__(0, "Y"*91), "上限 90"),
    ("标题重复", lambda p: p['groups'][0]['headlines'].__setitem__(1, p['groups'][0]['headlines'][0]), "重复"),
    ("全大写拒绝", lambda p: p['groups'][0]['headlines'].__setitem__(2, "FACTORY DIRECT SUPPLIER"), "全大写"),
    ("免邮违禁", lambda p: p['groups'][0]['callouts'].__setitem__(0, "Free Shipping"), "免邮"),
    ("虚假陈述#1", lambda p: p['groups'][0]['headlines'].__setitem__(3, "#1 Battery Supplier"), "虚假陈述"),
    ("危险品词", lambda p: p['groups'][0]['callouts'].__setitem__(1, "Hazardous Materials"), "危险品"),
    ("电话号", lambda p: p['groups'][0]['callouts'].__setitem__(2, "Call 555-123-4567"), "电话"),
    ("邮箱", lambda p: p['groups'][0]['callouts'].__setitem__(3, "sales@hiitio.com"), "邮箱"),
    ("装饰符号", lambda p: p['groups'][0]['headlines'].__setitem__(4, "★★★★ Best Supplier"), "装饰符号"),
    ("连续标点", lambda p: p['groups'][0]['descriptions'].__setitem__(1, "Best supplier ever!!!"), "标点"),
    ("纯CTA", lambda p: p['groups'][0]['headlines'].__setitem__(5, "Click Here"), "纯 CTA"),
    ("站内链接行超35", lambda p: p['groups'][0]['sitelinks'][0].__setitem__('line1', "Z"*36), "上限 35"),
    ("宣传信息<4条", lambda p: p['groups'][0].__setitem__('callouts', ["A","B","C"]), "最低展示要求"),
    ("摘要标题非法", lambda p: p['groups'][0]['snippets'][0].__setitem__('header', "Our Products"), "固定清单"),
    ("摘要值<3", lambda p: p['groups'][0]['snippets'][1].__setitem__('values', ["One","Two"]), "需 3"),
    ("路径超15", lambda p: p['groups'][0].__setitem__('paths', ["a"*16]), "上限 15"),
    ("路径含空格", lambda p: p['groups'][0].__setitem__('paths', ["hv dc"]), "空格"),
    # 通用性：换品牌/行业后必须仍能跑通（品牌名不得被误判）
]

# 通用性用例：虚构品牌 + 完全不同的行业（咖啡设备），验证 skill 不绑定任何具体站点
def make_generic(p):
    p['brand'] = 'ACME-ESPRESSO'
    p['site'] = 'https://example.com'
    p['target_audience'] = '咖啡馆采购与设备经销商'
    g = p['groups'][0]
    g['group_name'] = 'Commercial Espresso Machine'
    g['keywords'] = ['commercial espresso machine', 'cafe espresso maker']
    g['headlines'] = [
        "Commercial Espresso Machine", "Cafe Espresso Maker Supplier",
        "Factory Direct, No Middleman", "OEM Branding Available",
        "Certified for Commercial Use", "Request a Demo Today",
        "Get Spec Sheets Instantly", "Talk to Our Technicians",
        "Compare Boiler Configurations", "Download Pricing Guide",
        "Dual Boiler Heat Stability", "Stainless Steel Build",
        "NSF Certified Components", "ACME-ESPRESSO",
        "Book a Showroom Visit", "Pump Pressure Precisely Set",
        "Service Network Included", "Low Maintenance Design",
    ]
    g['descriptions'] = [
        "Commercial espresso machines for cafes and restaurants. NSF certified parts.",
        "Factory-direct supply with OEM branding options. Quotes within one business day.",
        "Dual boiler design holds brew temperature within tight tolerance at peak service.",
        "Supplying cafe operators and equipment dealers since 2009. Demo before volume.",
        "Custom voltage and plumbing configurations. Technicians help you specify.",
    ]
    g['paths'] = ['espresso', 'commercial']
    g['callouts'] = ["NSF Certified", "Factory Direct Pricing", "Demo Available",
                     "OEM Branding", "15 Years Experience"]
    g['sitelinks'][0].update({'text': "Espresso Machine Range",
                              'line1': "Compare boiler configurations",
                              'line2': "Filter by group size"})
    g['snippets'][0].update({'header': "Types",
                             'values': ["Dual Boiler", "Heat Exchange", "Single Group"]})
    g['snippets'][1].update({'header': "Features",
                             'values': ["PID Control", "Stainless Steel", "NSF Certified"]})
    p['groups'] = [g]

generic_case = ("通用性:虚构品牌异行业", make_generic, None)

print("=" * 72)
print("校验器能力验证")
print("=" * 72)

passed = 0
failed = []

for name, mutate, expect in cases + [generic_case]:
    p = json.loads(json.dumps(base))
    mutate(p)
    code, out = run(p)
    if expect is None:
        ok = code == 0
        detail = f"exit={code}"
    else:
        ok = (expect in out) and code == 1
        detail = f"exit={code}, 命中'{expect}'={'是' if expect in out else '否'}"
    mark = "PASS" if ok else "FAIL"
    if ok:
        passed += 1
    else:
        failed.append((name, detail, out[-400:]))
    print(f"[{mark}] {name:16} {detail}")

# 零售模式：free shipping 应放行
p = json.loads(json.dumps(base))
p['groups'][0]['callouts'][0] = "Free Shipping"
code, out = run(p, ["--retail"])
retail_ok = "免邮" not in out
print(f"[{'PASS' if retail_ok else 'FAIL'}] {'零售模式放行免邮':16} "
      f"exit={code}, 未报免邮={'是' if retail_ok else '否'}")
if retail_ok:
    passed += 1
else:
    failed.append(("零售模式", "仍报免邮", out[-300:]))

total = len(cases) + 2
print("\n" + "=" * 72)
print(f"结果：{passed}/{total} 通过")
if failed:
    print("\n失败项：")
    for n, d, o in failed:
        print(f"  - {n}: {d}")
        print("    " + o.replace("\n", "\n    "))
sys.exit(0 if not failed else 1)
