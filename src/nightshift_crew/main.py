"""入口：命令行运行创作 Crew"""

import sys

from nightshift_crew.crew import NightshiftCrew


def run():
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    if not prompt:
        print("用法：nightshift <你的任务>")
        print()
        print("示例：")
        print('  nightshift "设计 Day 2 的游戏机制，要求测试证据协作能力"')
        print('  nightshift "写一个场景：Day 6 终局，女友主动握住笔"')
        print('  nightshift "讨论：锚定后的意识状态应该怎么设定"')
        print('  nightshift "这个设定有没有逻辑漏洞：入侵者必须骗你违规才能攻击"')
        sys.exit(0)

    result = NightshiftCrew().crew().kickoff(inputs={"prompt": prompt})
    print(result)


if __name__ == "__main__":
    run()
