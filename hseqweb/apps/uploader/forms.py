from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from uploader.utils import FORM_ITEMS, hg19_to_hg38
from uploader.models import Upload
from uploader.qc_metadata import qc_metadata
from uploader.qc_fasta import qc_fasta
from django.forms import ValidationError
from uploader.tasks import upload_to_arvados
from .tusfile import TusFile
import tempfile
import json
import datetime
import os
from django.conf import settings
import gzip

UPLOADER_PROJECT_UUID = getattr(settings, 'UPLOADER_PROJECT_UUID', 'cborg-j7d0g-nyah4ques5ww7pk')

def is_gzip_file(filepath):
    with gzip.open(filepath) as f:
        try:
            f.read(1)
            return True
        except Exception:
            return False

def add_clean_field(cls, field_name):
    def required_field(self):
        metadata_file = self.cleaned_data.get('metadata_file', None)
        value = self.cleaned_data[field_name]
        if metadata_file is not None:
            return value
        if not value:
            raise ValidationError("This field is required.")
        return value

    required_field.__doc__ = "Required field validator for %s" % field_name
    required_field.__name__ = "clean_%s" % field_name
    setattr(cls, required_field.__name__, required_field)

class UploadForm(forms.ModelForm):
    ASSEMBLIES=[('GRCh38', 'GRCh38 (hg38)'), ('GRCh37', 'GRCh37 (hg19)')]

    sequence_file = forms.FileField(required=False,
        help_text='Sequence file in FASTQ format.')
    sequence_file_location = forms.CharField(required=False)
    sequence_file_filename = forms.CharField(required=False)
    sequence_file2 = forms.FileField(
        required=False,
        help_text='Optional FASTQ format file for paired reads.')
    sequence_file2_location = forms.CharField(required=False)
    sequence_file2_filename = forms.CharField(required=False)
    bed_file = forms.FileField(
        required=False,
        help_text='Optional BED format file for exome uploads.')
    bed_file_location = forms.CharField(required=False)
    bed_file_filename = forms.CharField(required=False)
    assembly = forms.ChoiceField(
        choices=ASSEMBLIES, 
        widget=forms.RadioSelect, 
        initial='GRCh38',
        required=False,
        help_text='Assembly version of Bed format file')
    metadata_file = forms.FileField(
        required=False,
        help_text='Metadata file in JSON/YAML format. Metadata fields are not required if this file is provided.')

    class Meta:
        model = Upload
        fields = []

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UploadForm, self).__init__(*args, **kwargs)
        for item in FORM_ITEMS: 
            if 'id' not in item:
                continue
            help_text = item.get('docstring', '')
            label = item['label']
            if item['required']:
                label += ' *'
            if item['type'] == 'text':
                if not item['list']:
                    self.fields[item['id']] = forms.CharField(
                        max_length=255, label=label,
                        help_text=help_text, required=False)
                else:
                    self.fields[item['id']] = SimpleArrayField(
                        forms.CharField(
                            max_length=255, required=False),
                        label=label, help_text=help_text, required=False)
            elif item['type'] == 'select':
                if not item['list']:
                    self.fields[item['id']] = forms.ChoiceField(
                        label=label, help_text=help_text, required=False,
                        choices=item['options'])
                else:
                    self.fields[item['id']] = SimpleArrayField(
                        forms.CharField(
                            max_length=255, required=False),
                        label=label, help_text=help_text, required=False,
                        widget=forms.Select(choices=item['options']))
            elif item['type'] == 'number':
                if not item['list']:
                    self.fields[item['id']] = forms.DecimalField(
                        label=label, help_text=help_text, required=False)
                else:
                    self.fields[item['id']] = SimpleArrayField(
                        forms.DecimalField(required=False),
                        label=label, help_text=help_text, required=False)
            elif item['type'] == 'date':
                if not item['list']:
                    self.fields[item['id']] = forms.DateField(
                        label=label, input_formats=['%m/%d/%Y',],
                        help_text=help_text, required=False)
                else:
                    self.fields[item['id']] = SimpleArrayField(
                        forms.DateField(
                            input_formats=['%m/%d/%Y',], required=False),
                        label=label, help_text=help_text, required=False)
            if item['required']:
                add_clean_field(UploadForm, item['id'])
            
            self.is_paired = False

    def file_fields(self):
        return [self['metadata_file']]

    def all_fields(self):
        for name in self.fields:
            if name.startswith('metadata.'):
                yield self[name]

    def clean_metadata_file(self):
        metadata_file = self.cleaned_data['metadata_file']
        if metadata_file:
            if not qc_metadata(metadata_file.temporary_file_path()):
                raise ValidationError("Invalid metadata format")    
        return metadata_file

    # def clean_sequence_file(self):
    #     sequence_file = self.cleaned_data['sequence_file']
    #     try:
    #         sf = open(sequence_file.temporary_file_path(), 'r')
    #         filename = qc_fasta(sf)
    #         self.is_fasta = filename == 'sequence.fasta'
    #     except ValueError:
    #         raise ValidationError("Invalid file format")
    #     return sequence_file


    def clean_sequence_file_location(self):
        sequence_file_location = self.cleaned_data['sequence_file_location']
        if not sequence_file_location:
            raise ValidationError("This field is required.")
        filepath = os.path.join(settings.TUS_UPLOAD_DIR, sequence_file_location)
        if not os.path.exists(filepath):
            raise ValidationError("Something went wrong! Make sure reads are different!")
        try:
            if is_gzip_file(filepath):
                sf = gzip.open(filepath, 'r')
            else:
                raise ValidationError("Files should be compressed with gzip!")
            qc_fasta(sf)
        except ValueError:
            raise ValidationError("Invalid file format")
        return sequence_file_location

    def clean_sequence_file_filename(self):
        sequence_file_filename = self.cleaned_data['sequence_file_filename']
        self.is_fasta = sequence_file_filename == 'sequence.fasta'
        return sequence_file_filename

    # def clean_sequence_file2(self):
    #     sequence_file2 = self.cleaned_data['sequence_file2']
    #     self.is_paired = False
    #     if sequence_file2:
    #         try:
    #             sf = open(sequence_file2.temporary_file_path(), 'r')
    #             filename = qc_fasta(sf)
    #             if filename != 'reads.fastq':
    #                 raise ValidationError('Invalid file format')
    #             self.is_paired = True
    #         except ValueError:
    #             raise ValidationError("Invalid file format")

    def clean_sequence_file2_location(self):
        sequence_file2_location = self.cleaned_data['sequence_file2_location']
        self.is_paired = False
        if sequence_file2_location:
            filepath = os.path.join(settings.TUS_UPLOAD_DIR, sequence_file2_location)
            if not os.path.exists(filepath):
                raise ValidationError("Something went wrong! Make sure reads are different!")
            try:
                if is_gzip_file(filepath):
                    sf = gzip.open(filepath, 'r')
                else:
                    raise ValidationError("Files should be compressed with gzip!")
                qc_fasta(sf)
                self.is_paired = True
            except ValueError:
                raise ValidationError("Invalid file format")

        return sequence_file2_location

    
    def clean_sequence_file2_filename(self):
        sequence_file2_filename = self.cleaned_data['sequence_file2_filename']
        # if sequence_file2_filename != 'reads.fastq':
        #     raise ValidationError('Invalid file format')
        # self.is_paired = True
        return sequence_file2_filename

    def clean_bed_file_location(self):
        bed_file_location = self.cleaned_data['bed_file_location']
        self.is_exome = False
        if bed_file_location:
            filepath = os.path.join(settings.TUS_UPLOAD_DIR, bed_file_location)
            if not os.path.exists(filepath):
                raise ValidationError("Something went wrong! Make sure reads are different!")
            try:
                bf = open(filepath, 'r')
                # TODO: check file format
                bf.close()
                self.is_exome = True
            except ValueError:
                raise ValidationError("Invalid file format")

        return bed_file_location

    
    def clean_bed_file_filename(self):
        bed_file_filename = self.cleaned_data['bed_file_filename']
        # if sequence_file2_filename != 'reads.fastq':
        #     raise ValidationError('Invalid file format')
        # self.is_paired = True
        return bed_file_filename

    def clean(self):
        if not self.cleaned_data.get('metadata_file', None):
            metadata = {}
            for key, val in self.cleaned_data.items():
                if not key.startswith('metadata') or not val:
                    continue
                if isinstance(val, datetime.date):
                    val = val.strftime('%Y-%m-%d')
                keys = key.split('.')
                if len(keys) == 2:
                    metadata[keys[1]] = val
                elif len(keys) == 3:
                    if keys[1] not in metadata:
                        metadata[keys[1]] = {}
                    metadata[keys[1]][keys[2]] = val
            metadata_str = json.dumps(metadata)
            f = tempfile.NamedTemporaryFile('wt', delete=False)
            f.write(metadata_str)
            f.close()

            if not qc_metadata(f.name):
                os.remove(f.name)
                raise ValidationError("Invalid metadata format")
            self.cleaned_data['fields_metadata_file'] = f.name
        if self.is_paired and self.is_fasta:
            raise ValidationError("Both files need to be in FASTQ format. Provide only one FASTA file otherwise")
        return self.cleaned_data
    

    def save_file(self, f):
        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        for chunk in f.chunks():
            tmp_file.write(chunk)
        tmp_file.close()
        return tmp_file.name        

    def save(self):
        self.instance = super(UploadForm, self).save(commit=False)
        self.instance.is_paired = self.is_paired
        self.instance.is_exome = self.is_exome
        if self.request.user.is_authenticated:
            self.instance.user = self.request.user
        # sequence_file = self.save_file(self.cleaned_data['sequence_file'])
        # sequence_file2 = self.cleaned_data['sequence_file2']
        # if sequence_file2:
        #     sequence_file2 = self.save_file(sequence_file2)

        sequence_file_loc = self.cleaned_data['sequence_file_location']
        sequence_filename = self.cleaned_data['sequence_file_filename']

        sequence_tus_file = TusFile(str(sequence_file_loc))
        sequence_tus_file.clean()
        # os.renames(os.path.join(settings.TUS_UPLOAD_DIR, sequence_file_loc), os.path.join(settings.TUS_UPLOAD_DIR, sequence_filename))
        sequence_file = os.path.join(settings.TUS_UPLOAD_DIR, sequence_file_loc)

        sequence_file_loc2 = self.cleaned_data['sequence_file2_location']
        sequence_filename2 = self.cleaned_data['sequence_file2_filename']
        sequence_file2 = None
        if sequence_file_loc != sequence_file_loc2 and sequence_file_loc2 and sequence_filename2:
            sequence_tus_file2 = TusFile(str(sequence_file_loc2))
            sequence_tus_file2.clean()
            # os.renames(os.path.join(settings.TUS_UPLOAD_DIR, sequence_file_loc2), os.path.join(settings.TUS_UPLOAD_DIR, sequence_filename2))
            sequence_file2 = os.path.join(settings.TUS_UPLOAD_DIR, sequence_file_loc2)

        bed_file_loc = self.cleaned_data['bed_file_location']
        bed_filename = self.cleaned_data['bed_file_filename']
        bed_file = None
        original_bed_file_grch37 = None
        if bed_file_loc and bed_filename:
            bed_tus_file = TusFile(str(bed_file_loc))
            bed_tus_file.clean()
            # os.renames(os.path.join(settings.TUS_UPLOAD_DIR, sequence_file_loc2), os.path.join(settings.TUS_UPLOAD_DIR, sequence_filename2))
            bed_file = os.path.join(settings.TUS_UPLOAD_DIR, bed_file_loc)
            print("Bed file assembly:", self.cleaned_data['assembly'])
            if bed_file and self.cleaned_data['assembly'] == 'GRCh37':
                bed_hg38_out_file = tempfile.NamedTemporaryFile('wt', delete=False)
                hg19_to_hg38(bed_file, bed_hg38_out_file.name)
                print("bed file conversion from hg19 to hg38 completed:", bed_file, bed_hg38_out_file.name)
                # if bed_file:
                #     os.remove(bed_file)
                original_bed_file_grch37 = bed_file
                bed_file = bed_hg38_out_file.name

        metadata_file = self.cleaned_data['metadata_file']
        if metadata_file:
            metadata_file = self.save_file(metadata_file)
        else:
            metadata_file = self.cleaned_data['fields_metadata_file']

        with open(metadata_file, 'r') as file_obj:
            # setting patient id
            metadata_content = json.load(file_obj)
            self.instance.patient_id = metadata_content['id']

        if not self.instance.id:
            self.instance.save()

        project_uuid = UPLOADER_PROJECT_UUID
        if self.request.user.userprofile.project_uuid:
            project_uuid = self.request.user.userprofile.project_uuid
        upload_to_arvados.delay(
            project_uuid,
            self.instance.id,
            sequence_file,
            sequence_file2,
            bed_file,
            original_bed_file_grch37,
            metadata_file)
        return self.instance
