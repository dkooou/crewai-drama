"""CLI entry — run the dream team with any prompt."""

import sys

from nightshift_crew.crew import NightshiftCrew


def run():
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    if not prompt:
        print("Usage: nightshift <your task>")
        print()
        print("Examples:")
        print('  nightshift "Design the season arc for a rule-horror series set in an office building"')
        print('  nightshift "Write the opening scene of E3: the protagonist discovers the lock has changed"')
        print('  nightshift "Review this premise for logic holes: the entity can only enter through open doors"')
        print('  nightshift "What horror short dramas are trending on TikTok this week?"')
        sys.exit(0)

    result = NightshiftCrew().crew().kickoff(inputs={"prompt": prompt})
    print(result)


if __name__ == "__main__":
    run()
