import os
import re
import subprocess
import sys
import time
from datetime import datetime

# 样式定义
COLORS = {
    "reset": "\033[0m",
    "cyan": "\033[96m",
    "green": "\033[92m",
    "red": "\033[91m",
    "bold": "\033[1m"
}

STYLES = {
    "info": f"{COLORS['cyan']}ℹ️  INFO{COLORS['reset']}",
    "success": f"{COLORS['green']}✅ SUCCESS{COLORS['reset']}",
    "error": f"{COLORS['red']}❌ ERROR{COLORS['reset']}",
    "divider": f"{COLORS['cyan']}{'='*60}{COLORS['reset']}"
}

def print_status(style, message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {style}: {message}")

def get_config_path():
    """获取配置文件路径（与原脚本逻辑一致）"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(script_dir, "dnsmasq-china-list")
    config_path = os.path.join(target_dir, "accelerated-domains.china.conf")
    
    if not os.path.exists(config_path):
        print_status(STYLES['error'], f"配置文件不存在: {config_path}")
        return None
    return config_path

def is_top_domain(line):
    """精确匹配.server=/*.xn--fiqs8s/格式的行"""
    line = line.strip()
    if not line.startswith("server=/"):
        return False
    return re.match(r'^server=/.*\.xn--fiqs8s/114\.114\.114\.114$', line)

# 新增中文检测函数
def contains_chinese(line):
    """检测域名部分包含中文字符的行"""
    line = line.strip()
    # 增加server=/前缀检查
    if not line.startswith("server=/"):
        return False
    # 精确提取域名部分（两个/之间的内容）
    domain_part = line.split('/')[1]
    # 扩展中文Unicode范围（包含基本汉字和扩展A区）
    return re.search(r'[\u4e00-\u9fff\u3400-\u4dbf]', domain_part)

def main():
    config_path = get_config_path()
    if not config_path:
        return

    target_dir = os.path.dirname(config_path)
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        removed = 0
        original_lines = lines.copy()
        for i, line in enumerate(original_lines):
            # 原有处理.xn--fiqs8s域名的逻辑
            if is_top_domain(line):
                domain = line.split('/')[1].rstrip('/')
                new_lines = [l for l in lines if l != line]
                
                # 写入修改后的配置
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                    f.flush()
                    os.fsync(f.fileno())
                
                time.sleep(0.5)

                # 提交包含中文的行
                subprocess.run(
                    ['git', 'add', 'accelerated-domains.china.conf'],
                    cwd=target_dir,
                    check=True
                )
                
            if contains_chinese(line):  # 将elif改为独立if判断
                domain = line.split('/')[1].rstrip('/')
                # 添加重复行检查
                if line not in lines:
                    continue
                new_lines = [l for l in lines if l != line]
                
                # 写入修改后的配置
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                    f.flush()
                    os.fsync(f.fileno())
                
                time.sleep(0.5)

                # 添加缺失的git add操作
                subprocess.run(
                    ['git', 'add', 'accelerated-domains.china.conf'],
                    cwd=target_dir,
                    check=True
                )
                # 保持commit操作不变
                subprocess.run(
                    ['git', 'commit', '-m', f'accelerated-domains: remove {domain}'],
                    cwd=target_dir,
                    check=True
                )
                
                print_status(STYLES['success'], f"已删除并提交: {domain}")
                removed += 1
                lines = new_lines
                time.sleep(1)

        print_status(STYLES['info'], f"共删除 {removed} 个域名（包含.xn--fiqs8s和中文字符）")  # 修改统计信息
        
    except Exception as e:
        print_status(STYLES['error'], f"处理失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        input("\n按回车键退出...")

if __name__ == "__main__":
    print(f"\n{STYLES['divider']}")
    print(f"{COLORS['bold']}DNSMASQ 中国域名清理工具{COLORS['reset']}")
    print(f"{STYLES['divider']}\n")
    main()

# 在文件顶部添加time模块导入
