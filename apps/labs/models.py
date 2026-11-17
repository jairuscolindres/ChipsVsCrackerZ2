import hashlib
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import check_password
from django.utils.translation import gettext_lazy as _


class Lab(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='labs')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, default='Firmware')
    points = models.IntegerField(default=100)
    wokwi_url = models.URLField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        app_label = 'labs'

    def __str__(self):
        return self.title

    def difficulty(self):
        if self.points <= 100:
            return 'Easy'
        elif self.points <= 300:
            return 'Medium'
        elif self.points <= 500:
            return 'Hard'
        return 'Deep-Fried'

    @property
    def tags(self):
        text = f"{self.title} {self.description or ''} {self.category}".lower()
        found_tags = []
        if 'esp32' in text:
            found_tags.append('ESP32-S3')
        elif 'avr' in text or 'arduino' in text:
            found_tags.append('AVR ATmega')
        elif 'stm32' in text or 'arm' in text:
            found_tags.append('ARM Cortex')
        elif 'rp2040' in text:
            found_tags.append('RP2040')
        else:
            found_tags.append('ESP32')

        if 'uart' in text or 'serial' in text:
            found_tags.append('UART')
        if 'i2c' in text:
            found_tags.append('I2C')
        if 'spi' in text:
            found_tags.append('SPI')
        if 'jtag' in text:
            found_tags.append('JTAG')
        if 'crypto' in text or 'encrypt' in text:
            found_tags.append('AES-XTS')
        if 'logic' in text or 'probe' in text:
            found_tags.append('Logic Analyzer')
        if 'bootloader' in text or 'rom' in text:
            found_tags.append('ROM Boot')

        if not found_tags:
            found_tags = [self.category, 'Hardware']
        return found_tags[:4]

    


class Flag(models.Model):
    lab = models.OneToOneField(Lab, on_delete=models.CASCADE, related_name='flag')
    flag_hash = models.CharField(max_length=255)
    is_case_sensitive = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'labs'

    def __str__(self):
        return f"Flag for {self.lab.title}"

    def check_flag(self, submitted_value: str) -> bool:
        if not submitted_value:
            return False
        val = submitted_value.strip()

        if val.startswith("FLAG{") and val.endswith("}"):
            full = val
            inner = val[5:-1]
        else:
            full = f"FLAG{{{val}}}"
            inner = val

        candidates = [full, inner, val]
        target = self.flag_hash.strip()

        for candidate in candidates:
            cand = candidate if self.is_case_sensitive else candidate.lower()
            targ = target if self.is_case_sensitive else target.lower()

            if cand == targ:
                return True

            cand_sha256 = hashlib.sha256(cand.encode('utf-8')).hexdigest()
            if cand_sha256.lower() == targ.lower():
                return True

            try:
                if check_password(cand, target):
                    return True
            except Exception:
                pass

        return False


class Submission(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='submissions')
    submitted_flag = models.TextField()
    is_correct = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'labs'

    def __str__(self):
        return f"{self.player.username} - {self.lab.title} - ({'Correct' if self.is_correct else 'Incorrect'})"


class Solve(models.Model):
    player = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solves')
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, related_name='solves')
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='solve')
    points_awarded = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'labs'
        constraints = [
            models.UniqueConstraint(fields=['player', 'lab'], name='unique_player_lab_solve')
        ]

    def __str__(self):
        return f"{self.player.username} solved {self.lab.title}"



