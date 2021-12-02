from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from six import b
from uploader.utils import api, parse_manifest_text
from datetime import date

COLLECTIONS_URL = 'https://collections.cborg.cbrc.kaust.edu.sa'

class OntologyClass(models.Model):
    uri = models.CharField(max_length=127, null=True)
    label = models.CharField(max_length=127)
class Pedigree(models.Model):
    identifier = models.CharField(max_length=63),
    father = models.ForeignKey('Patient', null=True, on_delete=models.SET_NULL, related_name='padigree_father')
    mother = models.ForeignKey('Patient', null=True, on_delete=models.SET_NULL, related_name='padigree_mother')
    sister = models.ForeignKey('Patient', null=True, on_delete=models.SET_NULL, related_name='padigree_sister')
    brother = models.ForeignKey('Patient', null=True, on_delete=models.SET_NULL, related_name='padigree_brother')
class PhenotypeFeature(models.Model):
    phenotype = models.ForeignKey(OntologyClass, on_delete=models.CASCADE, related_name='ontology_class')
    excluded = models.BooleanField(default=False)
class Patient(models.Model):
    MALE = 'male'
    FEMALE = 'female'
    UNKNOWN = 'unknown'
  
    GENDER_CHOICES = (
        (MALE, MALE),
        (FEMALE, FEMALE),
        (UNKNOWN, UNKNOWN)
    )
    identifier = models.CharField(max_length=63, unique=True, null=True)
    mrn = models.CharField(max_length=63, unique=True, null=True)
    first_name = models.CharField(max_length=127, null=True)
    last_name = models.CharField(max_length=127, blank=True, null=True)
    full_name = models.CharField(max_length=255, null=True)
    gender = models.CharField(max_length=31, choices=GENDER_CHOICES)
    date_of_birth = models.DateField(null=True)

    pedigree = models.ForeignKey(Pedigree, on_delete=models.CASCADE, related_name='pedigree', null=True)
    phenotypes = models.ManyToManyField(PhenotypeFeature)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_patients')
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='modified_patients')
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    @property
    def age(self):
        today = date.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class Upload(models.Model):
    SUBMITTED = "submitted"
    DRAFT = "draft"
    VALIDATED = "validated"
    ERROR = "error"
    UPLOADED = "uploaded"
    
    STATUSES = [
        (SUBMITTED, SUBMITTED),
        (DRAFT, DRAFT),
        (VALIDATED, VALIDATED),
        (ERROR, ERROR),
        (UPLOADED, UPLOADED)
    ]

    GRCh38 = 'GRCh38'
    GRCh37 = 'GRCh37'
    ASSEMBLIES = [
        (GRCh38, GRCh38),
        (GRCh37, GRCh37)
    ]

    is_trio = models.BooleanField(default=False)
    is_paired = models.BooleanField(default=False)
    is_exome = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, blank=True, null=True, on_delete=models.SET_NULL,
        related_name="uploads")
    date = models.DateTimeField(default=timezone.now)
    col_uuid = models.CharField(max_length=31, blank=True, null=True)
    status = models.CharField(
        max_length=15, default=SUBMITTED, choices=STATUSES)
    error_message = models.TextField(blank=True, null=True)

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='upload_patient', null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)

    sequence_file_location1 = models.CharField(max_length=127, blank=True, null=True)
    sequence_filename1 = models.CharField(max_length=127, blank=True, null=True)
    sequence_file_location2 = models.CharField(max_length=127, blank=True, null=True)
    sequence_filename2 = models.CharField(max_length=127, blank=True, null=True)
    bed_file_location = models.CharField(max_length=127, blank=True, null=True)
    bed_filename = models.CharField(max_length=127, blank=True, null=True)
    assembly = models.CharField(max_length=15, default=GRCh38, choices=ASSEMBLIES)

    father_sequence_file_location1 = models.CharField(max_length=127, blank=True, null=True)
    father_sequence_filename1 = models.CharField(max_length=127, blank=True, null=True)
    father_sequence_file_location2 = models.CharField(max_length=127, blank=True, null=True)
    father_sequence_filename2 = models.CharField(max_length=127, blank=True, null=True)
    father_bed_file_location = models.CharField(max_length=127, blank=True, null=True)
    father_bed_filename = models.CharField(max_length=127, blank=True, null=True)
    father_assembly = models.CharField(max_length=15, default=GRCh38, choices=ASSEMBLIES)
    is_paired_father = models.BooleanField(default=False)
    is_exome_father = models.BooleanField(default=False)


    mother_sequence_file_location1 = models.CharField(max_length=127, blank=True, null=True)
    mother_sequence_filename1 = models.CharField(max_length=127, blank=True, null=True)
    mother_sequence_file_location2 = models.CharField(max_length=127, blank=True, null=True)
    mother_sequence_filename2 = models.CharField(max_length=127, blank=True, null=True)
    mother_bed_file_location = models.CharField(max_length=127, blank=True, null=True)
    mother_bed_filename = models.CharField(max_length=127, blank=True, null=True)
    mother_assembly = models.CharField(max_length=15, default=GRCh38, choices=ASSEMBLIES)
    is_paired_mother = models.BooleanField(default=False)
    is_exome_mother = models.BooleanField(default=False)

    sibling_sequence_file_location1 = models.CharField(max_length=127, blank=True, null=True)
    sibling_sequence_filename1 = models.CharField(max_length=127, blank=True, null=True)
    sibling_sequence_file_location2 = models.CharField(max_length=127, blank=True, null=True)
    sibling_sequence_filename2 = models.CharField(max_length=127, blank=True, null=True)
    sibling_bed_file_location = models.CharField(max_length=127, blank=True, null=True)
    sibling_bed_filename = models.CharField(max_length=127, blank=True, null=True)
    sibling_assembly = models.CharField(max_length=15, default=GRCh38, choices=ASSEMBLIES)
    is_paired_sibling = models.BooleanField(default=False)
    is_exome_sibling = models.BooleanField(default=False)

    phenotypes_snapshot = models.CharField(max_length=1024, blank=True, null=True)
    pedigree_snapshot = models.CharField(max_length=1024, blank=True, null=True)

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
    def output_status(self):
        if self.collection and 'analysis_complete' in self.collection['properties']:
            return 'complete'
        return 'in progress'

    @property
    def output_collection(self):
        if self.output_status != 'complete':
            return None
        if hasattr(self, '_out_col'):
            return self._out_col
        try:
            self._out_col = api.collections().get(
                uuid=self.out_col_uuid).execute()
            return self._out_col
        except Exception:
            pass
        return None

    @property
    def out_col_uuid(self):
        if self.collection and 'output_collection' in self.collection['properties']:
            return self.collection['properties']['output_collection']
        return None
        
    @property
    def output_files(self):
        if not self.output_collection:
            return []
        return parse_manifest_text(self.output_collection['manifest_text'])


    @property
    def name(self):
        if not self.collection:
            return None
        return self.collection['properties']['id']

    @property
    def files(self):
        if not self.collection:
            return []
        return parse_manifest_text(self.collection['manifest_text'])

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
    
