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
    """精确匹配.server=/*.top/格式的行"""
    line = line.strip()
    if not line.startswith("server=/"):
        return False
    # 修复正则表达式匹配逻辑
    return re.match(r'^server=/.*\.top/114\.114\.114\.114$', line)  # <mcsymbol name="is_top_domain" filename="remove_top_domains.py" path="e:\Github\remove_top_domains.py" startline="34" type="function"></mcsymbol>

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
            if is_top_domain(line):
                domain = line.split('/')[1].rstrip('/')
                new_lines = [l for l in lines if l != line]
                
                # 修复1：移除newline参数，添加文件同步
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                    f.flush()  # 强制刷新缓冲区
                    os.fsync(f.fileno())  # 确保写入磁盘
                
                # 新增延迟防止文件锁冲突
                time.sleep(0.5)  # 适当缩短等待时间

                # 修复git操作
                subprocess.run(
                    ['git', 'add', 'accelerated-domains.china.conf'],
                    cwd=target_dir,
                    check=True
                )
                subprocess.run(
                    ['git', 'commit', '-m', f'accelerated-domains: remove {domain}'],
                    cwd=target_dir,
                    check=True
                )
                
                print_status(STYLES['success'], f"已删除并提交: {domain}")
                removed += 1
                lines = new_lines
                time.sleep(1)  # 新增提交后等待

        print_status(STYLES['info'], f"共删除 {removed} 个.top域名")
        
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
