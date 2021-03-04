from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from uploader.utils import api
COLLECTIONS_URL = 'https://collections.cborg.cbrc.kaust.edu.sa'


class Upload(models.Model):
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    ERROR = "error"
    UPLOADED = "uploaded"
    
    STATUSES = [
        (SUBMITTED, SUBMITTED),
        (VALIDATED, VALIDATED),
        (ERROR, ERROR),
        (UPLOADED, UPLOADED)
    ]
    is_fasta = models.BooleanField(default=True)
    is_paired = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL,
        related_name="uploads")
    date = models.DateTimeField(default=timezone.now)
    col_uuid = models.CharField(max_length=31, blank=True, null=True)
    status = models.CharField(
        max_length=15, default=SUBMITTED, choices=STATUSES)
    error_message = models.CharField(max_length=255, blank=True, null=True)

    @property
    def collection(self):
        if not self.col_uuid:
            return None
        if hasattr(self, '_col'):
            return self._col
        try:
            self._col = api.collections().get(uuid=self.col_uuid).execute()
            return self._col
        except Exception:
            pass
        return None

    @property
    def name(self):
        if not self.collection:
            return None
        return self.collection['properties']['sequence_label']

    @property
    def sequence_filename(self):
        if self.is_fasta:
            return 'sequence.fasta'
        return 'reads.fastq'

    @property
    def metadata_filename(self):
        return 'metadata.yaml'

    @property
    def token(self):
        if self.user:
            return self.user.userprofile.token
        return None
    
