from django.db import models


class Technology(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, null=True)
    cover_img = models.URLField(null=True)
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Technologies'

    def __str__(self) -> str:
        return self.title


class Resource(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000, null=True)
    url = models.URLField()
    is_free = models.BooleanField(default=True)
    technology = models.ForeignKey(Technology, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.title


class FeaturedCode(models.Model):
    PLAIN_TEXT = 'TXT'
    JAVASCRIPT = 'JS'
    PYTHON = 'PY'
    TYPESCRIPT = 'TS'
    PHP = 'PHP'
    CSS = 'CSS'
    LANGUAGES_CHOICES = [
        (PLAIN_TEXT, 'Plain Text'),
        (JAVASCRIPT, 'JavaScript'),
        (PYTHON, 'Python'),
        (TYPESCRIPT, 'TypeScript'),
        (PHP, 'PHP'),
        (CSS, 'CSS'),
    ]

    code = models.TextField(max_length=255)
    language = models.CharField(
        max_length=3,
        choices=LANGUAGES_CHOICES,
        default=PLAIN_TEXT
    )
    technology = models.OneToOneField(Technology, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"[{self.language}]: {self.code[:15]}..."
