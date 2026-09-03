import re

LOG_FILE = "brilcalc.log"

def main():
    with open(LOG_FILE) as f:
        content = f.read()

    summary_section = content.split("#Summary:")[1]

    pattern = (
        r"\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|"
        r"\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|"
    )
    match = re.search(pattern, summary_section)

    totrecorded_pb = float(match.group(6))
    totrecorded_fb = totrecorded_pb / 1000.0

    print(f"Luminosidade integrada: {totrecorded_fb:.1f} fb^-1")

if __name__ == "__main__":
    main()
