"""入口：运行《夜班守则》创作 Crew"""

from nightshift_crew.crew import NightshiftCrew


def run():
    """默认运行：游戏机制设计全流程（编剧→视觉→审核）"""
    inputs = {
        "day_number": "Day 2",
        "previous_day_summary": "Day 1 是边界识别测试——通过工牌闸机游戏，测试参与者能否在压力下准确识别哪些行为构成违规。林深通过观察闸机的判定延迟找到了漏洞。",
        "constraint": "需要测试证据协作能力——参与者必须合作收集证据，但证据可能被伪造",
    }
    NightshiftCrew().crew().kickoff(inputs=inputs)


def scene():
    """单场景创作"""
    inputs = {
        "scene_brief": "Day 6 终局。女友被入侵者力量击中，意识即将锚定。她主动握住林深手中的笔。林深通过 Day 5 获得的授权，合法带着笔离开。最后一幕：笔尖微颤，缓慢写出"还在"。",
    }
    NightshiftCrew().crew().kickoff(inputs=inputs)


def discuss():
    """世界观讨论"""
    inputs = {
        "question": "锚定后的意识状态应该怎么设定？目前倾向"功能人格"——不被使用时是人，被使用时被强制变成好用的东西，始终记得两种状态。还有更好的方案吗？",
    }
    NightshiftCrew().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    run()
