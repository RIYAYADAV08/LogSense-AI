"""Generate a sample log with a normal baseline and an injected incident."""
import random

random.seed(7)
services = ["nginx", "sshd", "mysql", "app"]
lines = []
for minute in range(60):
    hh, mm = divmod(minute, 60)
    for _ in range(random.randint(8, 14)):
        lvl = random.choices(["INFO", "WARN", "ERROR"], [90, 8, 2])[0]
        svc = random.choice(services)
        sec = random.randint(0, 59)
        lines.append(f"2026-10-01 10:{minute:02d}:{sec:02d} {lvl} {svc} request handled")
    if minute in (41, 42):  # injected incident: mysql failing + brute force
        for _ in range(40):
            sec = random.randint(0, 59)
            lines.append(f"2026-10-01 10:{minute:02d}:{sec:02d} ERROR mysql connection refused")
            lines.append(f"2026-10-01 10:{minute:02d}:{sec:02d} WARN sshd Failed password for root")
open("sample.log", "w").write("\n".join(sorted(lines)))
print("sample.log written with", len(lines), "lines")
