from django.shortcuts import render


# ──────────────────────────────────────────────────────────
#  Lab registry — each entry maps to a Wokwi project embed
#  Replace WOKWI_PROJECT_ID with your actual project IDs
# ──────────────────────────────────────────────────────────
LABS = {
    "001-leaky-uart": {
        "title": "Leaky UART — SmartLock Debug Dump",
        "difficulty": "Easy",
        "difficulty_color": "green",
        "points": 250,
        "arch_tags": ["ESP32", "UART", "EEPROM"],
        "brief": (
            "A prototype IoT smart-lock controller has been deployed with debug "
            "logging still enabled. The developers left verbose UART output active, "
            "and the device dumps sensitive EEPROM contents — including hardcoded "
            "master credentials — over its serial TX line every time it boots.\n\n"
            "Your mission: Tap into the UART bus, observe the boot sequence in the "
            "Serial Monitor, and extract the leaked authentication flag."
        ),
        "datasheet": {
            "pins": [
                ("GPIO1 (TX)", "UART Transmit", "OUT"),
                ("GPIO3 (RX)", "UART Receive", "IN"),
                ("GPIO2", "Status LED (Blue)", "OUT"),
                ("GPIO4", "Lock LED (Red)", "OUT"),
                ("GPIO5", "Unlock LED (Green)", "OUT"),
            ],
            "baud": "115200",
        },
        "hints": [
            "The device prints everything to Serial on boot — just watch the output.",
            "Look for lines tagged [ DBG ] — those are the debug messages the devs forgot to remove.",
            "The flag format is FLAG{...}. It's printed in plain text.",
        ],
        "flag": "d34d_b33f_c0ff33",
        # Wokwi project ID (just the numeric ID)
        "wokwi_project_id": "480289711537349633",
    },
}


def dev_lab_view(request, lab_slug="001-leaky-uart"):
    """Secret dev endpoint — no auth required, for testing the Wokwi canvas."""
    lab = LABS.get(lab_slug)
    if not lab:
        lab = LABS["001-leaky-uart"]

    context = {"lab": lab, "lab_slug": lab_slug}
    return render(request, "lab/workspace.html", context)
