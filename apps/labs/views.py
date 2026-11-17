import hashlib
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.utils.text import slugify
from labs.models import Lab, Flag, Submission, Solve


SAMPLE_FIRMWARE_CODE = """/*
 * ChipsvsCrackerZ - Industrial IoT Sensor Node v2.4
 * Target: ESP32-S3 (Xtensa Dual-Core @ 240MHz)
 * Flash: 4MB QSPI | Secure Boot: V2 | Crypto: Hardware AES-XTS
 * Serial: UART0 @ 115200 8-N-1 (GPIO43: TX, GPIO44: RX)
 */

#include <stdio.h>
#include <string.h>
#include "esp_system.h"
#include "driver/uart.h"
#include "soc/rtc_cntl_reg.h"

#define UART_NUM       UART_NUM_0
#define BUF_SIZE       1024
#define BAUD_RATE      115200

static const char* BOOT_BANNER = 
    "\\r\\n[CHIPS-V-CRACKERZ] DINER-SECURE IoT NODE BOOTLOADER v2.4\\r\\n"
    "[HW] MCU: ESP32-S3 (revision 1) | Silicon ID: 0x4E7F\\r\\n"
    "[HW] Crystal: 40MHz | CPU: 240MHz | VDD33: 3.28V (OK)\\r\\n"
    "[AUTH] Secure Boot Digest verified. OTP keys: LOCKED\\r\\n"
    "[UART] UART0 initialized at 115200 8N1.\\r\\n";

void uart_send_str(const char* str) {
    uart_write_bytes(UART_NUM, str, strlen(str));
}

void process_debug_command(char* cmd) {
    if (strncmp(cmd, "help", 4) == 0) {
        uart_send_str(
            "Available diagnostics:\\r\\n"
            "  help       - Print this telemetry help\\r\\n"
            "  status     - Query system bus & thermal registers\\r\\n"
            "  probe      - Probe I2C/SPI bus traces\\r\\n"
            "  dump_mem   - Extract non-volatile telemetry payload\\r\\n"
            "  reboot     - Trigger soft hardware watchdog reset\\r\\n"
        );
    } else if (strncmp(cmd, "status", 6) == 0) {
        uart_send_str(
            "[STATUS] Thermal: 37.4C | Core0: 12% | Core1: 4%\\r\\n"
            "[STATUS] Voltage rails: VCC=3.30V | VDD_A=1.80V\\r\\n"
            "[STATUS] Security state: ARMED (Tamper sensor: NORMAL)\\r\\n"
        );
    } else if (strncmp(cmd, "dump_mem", 8) == 0) {
        uart_send_str(
            "[DUMP] Reading encrypted flash sector @ 0x003F4000...\\r\\n"
            "[DUMP] 003F4000: 46 4C 41 47 7B 55 41 52 54 5F 42 34 55 44 5F 52 | FLAG{UART_B4UD_R\\r\\n"
            "[DUMP] 003F4010: 34 54 33 5F 50 57 4E 33 44 5F 37 33 33 31 7D 00 | 4T3_PWN3D_7331}.\\r\\n"
            "[DUMP] Telemetry extraction complete. Checksum CRC32: 0x9B2A4F10\\r\\n"
        );
    } else if (strncmp(cmd, "probe", 5) == 0) {
        uart_send_str(
            "[PROBE] Scanning GPIO pins...\\r\\n"
            "[PROBE] Pin 1  (TX0)  : HIGH (3.3V) [ACTIVE]\\r\\n"
            "[PROBE] Pin 3  (RX0)  : HIGH (3.3V) [LISTENING]\\r\\n"
            "[PROBE] Pin 21 (SDA)  : PULLUP 4.7k [IDLE]\\r\\n"
            "[PROBE] Pin 22 (SCL)  : CLK 100kHz [PULSING]\\r\\n"
        );
    } else if (strncmp(cmd, "reboot", 6) == 0) {
        uart_send_str("[SYS] Watchdog reset requested. Rebooting...\\r\\n");
        esp_restart();
    } else {
        uart_send_str("[ERR] Unknown command. Type 'help' for debug shell.\\r\\n");
    }
}

void app_main(void) {
    uart_config_t uart_config = {
        .baud_rate = BAUD_RATE,
        .data_bits = UART_DATA_8_BITS,
        .parity    = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE
    };
    uart_param_config(UART_NUM, &uart_config);
    uart_driver_install(UART_NUM, BUF_SIZE * 2, 0, 0, NULL, 0);

    uart_send_str(BOOT_BANNER);
    uart_send_str("> ");

    uint8_t data[BUF_SIZE];
    while (1) {
        int len = uart_read_bytes(UART_NUM, data, BUF_SIZE - 1, 20 / portTICK_PERIOD_MS);
        if (len > 0) {
            data[len] = '\\0';
            process_debug_command((char*)data);
            uart_send_str("> ");
        }
    }
}
"""

SAMPLE_DATASHEET = {
    'mcu': 'ESP32-S3-WROOM-1',
    'frequency': '240 MHz Dual-Core',
    'voltage': '3.3V DC (Operational range: 3.0V - 3.6V)',
    'flash': '4 MB Quad SPI Flash',
    'ram': '512 KB SRAM + 384 KB ROM',
    'pins': [
        {'pin': 'Pin 1', 'gpio': 'GPIO 43 / TXD0', 'type': 'Digital Out', 'level': '3.3V TTL', 'desc': 'Primary Serial Telemetry (Idle High)'},
        {'pin': 'Pin 3', 'gpio': 'GPIO 44 / RXD0', 'type': 'Digital In', 'level': '3.3V TTL', 'desc': 'Serial Diagnostic Injection Bus'},
        {'pin': 'Pin 4', 'gpio': 'GPIO 0 / BOOT', 'type': 'Strap Pin', 'level': '3.3V / GND', 'desc': 'Hold LOW on reset to trigger ROM Bootloader'},
        {'pin': 'Pin 21', 'gpio': 'GPIO 21 / SDA', 'type': 'Open-Drain', 'level': '3.3V Pullup', 'desc': 'I2C Telemetry Bus Data Line'},
        {'pin': 'Pin 22', 'gpio': 'GPIO 22 / SCL', 'type': 'Clock Out', 'level': '3.3V 100kHz', 'desc': 'I2C Telemetry Bus Clock Line'},
        {'pin': 'Pin 15', 'gpio': 'VCC (3V3)', 'type': 'Power', 'level': '+3.3V DC', 'desc': 'Main Regulated Power Supply Rail'},
        {'pin': 'Pin 16', 'gpio': 'GND', 'type': 'Ground', 'level': '0.0V', 'desc': 'Common Ground Reference Plane'}
    ],
    'registers': [
        {'addr': '0x0000_0000 - 0x0005_FFFF', 'name': 'ROM-BOOT', 'access': 'R', 'desc': 'Masked Bootloader ROM & Security Verifier'},
        {'addr': '0x3F40_0000 - 0x3F7F_FFFF', 'name': 'EXT-FLASH', 'access': 'R/W', 'desc': 'Encrypted QSPI Firmware & Calibration Payload'},
        {'addr': '0x6000_0000 - 0x6000_0FFF', 'name': 'UART0-CTRL', 'access': 'R/W', 'desc': 'UART0 Baud Rate Divisor, FIFO, and Status Regs'},
        {'addr': '0x6000_8000 - 0x6000_8FFF', 'name': 'RTC-CNTL', 'access': 'R/W', 'desc': 'Power management, reset cause, clock gating'}
    ]
}

SAMPLE_HINTS = [
    {
        'id': 1,
        'title': 'Baud Rate Calibration',
        'cost': 0,
        'unlocked': True,
        'difficulty': 'Easy',
        'body': 'Standard hardware bootloaders stream diagnostic logs at 115200 baud (8 data bits, no parity, 1 stop bit). If receiving garbled frames on your logic probe, calibrate your UART receiver clock.'
    },
    {
        'id': 2,
        'title': 'Interactive Bootloader Shell',
        'cost': 50,
        'unlocked': True,
        'difficulty': 'Medium',
        'body': 'The firmware listening loop accepts text commands over UART0. Send "help" to list diagnostic subroutines, or use "dump_mem" to extract the non-volatile memory sector.'
    },
    {
        'id': 3,
        'title': 'Payload Extraction & Verification',
        'cost': 100,
        'unlocked': True,
        'difficulty': 'Hard',
        'body': 'Memory sector 0x003F4000 holds the decrypted device telemetry payload formatted as FLAG{...}. Submit the payload through the hardware injector panel.'
    }
]


def lab_list_view(request):
    """
    Labs Library View: Component Inventory layout with architecture/difficulty filtering.
    """
    labs = Lab.objects.filter(is_published=True).order_by('points', 'id')

    user_solves = set()
    total_user_points = 0
    if request.user.is_authenticated:
        user_solves = set(
            Solve.objects.filter(player=request.user).values_list('lab_id', flat=True)
        )
        total_user_points = Solve.objects.filter(player=request.user).aggregate(
            total=models.Sum('points_awarded')
        )['total'] or 0

    query = request.GET.get('q', '').strip()
    selected_difficulty = request.GET.get('difficulty', '').strip()
    selected_status = request.GET.get('status', '').strip()

    if query:
        terms = query.split()
        for term in terms:
            if term.lower().startswith('arch:') or term.lower().startswith('tag:'):
                qualifier_val = term.split(':', 1)[1]
                labs = labs.filter(
                    models.Q(title__icontains=qualifier_val) |
                    models.Q(description__icontains=qualifier_val) |
                    models.Q(category__icontains=qualifier_val)
                )
            else:
                labs = labs.filter(
                    models.Q(title__icontains=term) |
                    models.Q(description__icontains=term) |
                    models.Q(category__icontains=term)
                )

    if selected_difficulty:
        diff_lower = selected_difficulty.lower()
        if diff_lower == 'easy':
            labs = labs.filter(points__lte=100)
        elif diff_lower == 'medium':
            labs = labs.filter(points__gt=100, points__lte=300)
        elif diff_lower == 'hard':
            labs = labs.filter(points__gt=300, points__lte=500)
        elif diff_lower in ('deep-fried', 'deepfried'):
            labs = labs.filter(points__gt=500)

    if selected_status:
        status_lower = selected_status.lower()
        if status_lower == 'solved':
            labs = labs.filter(id__in=user_solves)
        elif status_lower in ('unsolved', 'active'):
            labs = labs.exclude(id__in=user_solves)

    return render(request, 'labs/lab_list.html', {
        'labs': labs,
        'query': query,
        'selected_difficulty': selected_difficulty,
        'selected_status': selected_status,
        'user_solves': user_solves,
        'total_user_points': total_user_points,
    })


def lab_interface_view(request, slug):
    """
    Lab Interface View (Split Workbench):
    Left Panel: Interactive Workbench (Wokwi Virtual Hardware + Firmware Code Editor / UART Serial Monitor)
    Right Panel: Challenge Control (Brief, Datasheet, Hints, Flag Submission Payload Injector)
    Standard Django form POST for flag submission without AJAX.
    """
    lab = get_object_or_404(Lab, slug=slug)

    submission_result = None

    # Handle standard POST flag submission
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Authentication required. Please log in to submit payloads.')
            return redirect('login:login')

        raw_flag = request.POST.get('flag', '').strip()

        if not raw_flag:
            messages.error(request, 'Payload cannot be empty.')
            submission_result = {'status': 'error', 'message': 'Payload cannot be empty.'}
        else:
            has_flag = hasattr(lab, 'flag') and lab.flag is not None
            is_correct = lab.flag.check_flag(raw_flag) if has_flag else False

            # Record submission
            submission = Submission.objects.create(
                player=request.user,
                lab=lab,
                submitted_flag=raw_flag,
                is_correct=is_correct
            )

            if is_correct:
                solve, created = Solve.objects.get_or_create(
                    player=request.user,
                    lab=lab,
                    defaults={
                        'submission': submission,
                        'points_awarded': lab.points
                    }
                )
                if created:
                    messages.success(request, f'+{lab.points} PTS Awarded! Hardware exploit verified.')
                    submission_result = {
                        'status': 'success',
                        'points_awarded': lab.points,
                        'message': f'+{lab.points} PTS Awarded! Hardware exploit verified.'
                    }
                else:
                    messages.info(request, 'Payload verified (Challenge already solved).')
                    submission_result = {
                        'status': 'success',
                        'points_awarded': 0,
                        'message': 'Payload verified (Challenge already solved).'
                    }
            else:
                messages.error(request, 'Checksum mismatch or invalid payload')
                submission_result = {
                    'status': 'error',
                    'message': 'Checksum mismatch or invalid payload'
                }

    # Query solved state and statistics
    is_solved = False
    solve_record = None
    total_user_points = 0
    user_submissions = []

    if request.user.is_authenticated:
        solve_record = Solve.objects.filter(player=request.user, lab=lab).first()
        is_solved = solve_record is not None
        total_user_points = Solve.objects.filter(player=request.user).aggregate(
            total=models.Sum('points_awarded')
        )['total'] or 0
        user_submissions = Submission.objects.filter(
            lab=lab, player=request.user
        ).order_by('-created_at')[:10]

    solves_count = Solve.objects.filter(lab=lab).count()
    submissions_count = Submission.objects.filter(lab=lab).count()
    all_labs = Lab.objects.filter(is_published=True).only('id', 'title', 'slug', 'points')

    # Construct Wokwi embed URL
    wokwi_embed_url = lab.wokwi_url
    if wokwi_embed_url and 'wokwi.com/projects/' in wokwi_embed_url:
        if '?' not in wokwi_embed_url:
            wokwi_embed_url = f"{wokwi_embed_url}?view=diagram"

    context = {
        'lab': lab,
        'is_solved': is_solved,
        'solve_record': solve_record,
        'solves_count': solves_count,
        'submissions_count': submissions_count,
        'user_submissions': user_submissions,
        'total_user_points': total_user_points,
        'wokwi_embed_url': wokwi_embed_url,
        'firmware_code': SAMPLE_FIRMWARE_CODE,
        'datasheet': SAMPLE_DATASHEET,
        'hints': SAMPLE_HINTS,
        'all_labs': all_labs,
        'submission_result': submission_result,
    }

    return render(request, 'labs/lab_interface.html', context)


@login_required
def challenge_editor_view(request):
    """
    Challenge Authoring Studio / Lab Editor.
    Enables lab authors to design, wire, and configure new hardware CTF challenges.
    """
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category = request.POST.get('category', 'Hardware Interfacing').strip()
        try:
            points = int(request.POST.get('points', 100) or 100)
        except ValueError:
            points = 100
        wokwi_url = request.POST.get('wokwi_url', '').strip()
        description = request.POST.get('description', '').strip()
        flag_val = request.POST.get('flag', '').strip()
        is_published = request.POST.get('is_published') == 'on'

        if not title:
            messages.error(request, 'Challenge title cannot be empty.')
        elif not wokwi_url:
            messages.error(request, 'Wokwi project URL is required.')
        elif not flag_val:
            messages.error(request, 'Verification flag secret is required.')
        else:
            base_slug = slugify(title)
            slug = base_slug or 'hardware-lab'
            counter = 1
            while Lab.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            lab = Lab.objects.create(
                author=request.user,
                title=title,
                slug=slug,
                description=description,
                category=category,
                points=points,
                wokwi_url=wokwi_url,
                is_published=is_published,
            )

            # Store flag (store sha256 hash or raw)
            Flag.objects.create(
                lab=lab,
                flag_hash=flag_val,
                is_case_sensitive=True,
            )

            messages.success(request, f'Challenge "{title}" successfully synthesized and mounted to inventory.')
            return redirect('labs:lab_interface', slug=lab.slug)

    authored_labs = Lab.objects.filter(author=request.user).order_by('-created_at')
    all_labs_count = Lab.objects.count()

    total_user_points = 0
    if request.user.is_authenticated:
        total_user_points = Solve.objects.filter(player=request.user).aggregate(
            total=models.Sum('points_awarded')
        )['total'] or 0

    return render(request, 'labs/challenge_editor.html', {
        'authored_labs': authored_labs,
        'all_labs_count': all_labs_count,
        'total_user_points': total_user_points,
    })

