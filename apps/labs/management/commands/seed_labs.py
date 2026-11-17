from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from labs.models import Lab, Flag
import hashlib

class Command(BaseCommand):
    help = 'Seeds sample labs and flags for ChipsvsCrackerZ'

    def handle(self, *args, **options):
        author = User.objects.first()
        if not author:
            author = User.objects.create_user(username='admin', password='adminpassword')
            self.stdout.write(self.style.SUCCESS(f'Created default user {author.username}'))

        lab, created = Lab.objects.get_or_create(
            slug='esp32-uart-exploit-01',
            defaults={
                'author': author,
                'title': 'ESP32 UART Exploit & Bus Snooping',
                'description': (
                    'A compromised Deep-Fried Industrial IoT terminal was seized from the Diner circuit bench. '
                    'The target ESP32-S3 microcontroller is broadcasting encrypted telemetry on its primary UART0 bus. '
                    'Probe the TX/RX pins at 115200 baud, trigger the bootloader debug command sequence, and extract '
                    'the firmware encryption key payload.'
                ),
                'category': 'Firmware',
                'points': 500,
                'wokwi_url': 'https://wokwi.com/projects/344606822858064466',
                'is_published': True,
            }
        )

        flag_str = 'FLAG{UART_B4UD_R4T3_PWN3D_7331}'
        flag, flag_created = Flag.objects.get_or_create(
            lab=lab,
            defaults={
                'flag_hash': flag_str,
                'is_case_sensitive': True,
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created lab "{lab.title}"'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Lab "{lab.title}" already exists'))

        self.stdout.write(self.style.SUCCESS(f'Flag configured for "{lab.title}": {flag_str}'))

        # Lab 2: Simon Says Memory Sequence & Glitch Bypass
        simon_lab, simon_created = Lab.objects.get_or_create(
            slug='simon-memory-glitch-bypass',
            defaults={
                'author': author,
                'title': 'Simon Says: Memory Sequence & Glitch Bypass',
                'description': (
                    'An embedded microcontroller runs an interactive Simon sequence memory game with physical pushbuttons, '
                    'audio buzzer, and dynamic score counter. Reverse-engineer the hardware state machine or trigger a '
                    'memory sequence timing bypass to beat the high score threshold and extract the validation flag.'
                ),
                'category': 'Circuit Analysis',
                'points': 250,
                'wokwi_url': 'https://wokwi.com/projects/480289711537349633',
                'is_published': True,
            }
        )

        simon_flag_str = 'FLAG{S1M0N_S4YS_GL1TCH_TH3_M3M0RY_7331}'
        simon_flag, simon_flag_created = Flag.objects.get_or_create(
            lab=simon_lab,
            defaults={
                'flag_hash': simon_flag_str,
                'is_case_sensitive': True,
            }
        )

        if simon_created:
            self.stdout.write(self.style.SUCCESS(f'Created lab "{simon_lab.title}"'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Lab "{simon_lab.title}" already exists'))

        self.stdout.write(self.style.SUCCESS(f'Flag configured for "{simon_lab.title}": {simon_flag_str}'))
