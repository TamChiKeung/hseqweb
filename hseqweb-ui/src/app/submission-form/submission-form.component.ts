import { NgIf } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbDateStruct, NgbNavChangeEvent } from '@ng-bootstrap/ng-bootstrap';
import { NgbDateISOParserFormatter } from '@ng-bootstrap/ng-bootstrap/datepicker/ngb-date-parser-formatter';
import { NgSelectConfig } from '@ng-select/ng-select';
import { concat, Observable, of, Subject } from 'rxjs';
import { catchError, distinctUntilChanged, map, switchMap, tap } from 'rxjs/operators';
import { LookupService } from 'src/lookup.service';
import { PatientService } from 'src/patient.service';
import { SubmissionsService } from 'src/submission.service';
import { ToastService } from 'src/toast-service';


@Component({
  selector: 'app-submission-form',
  templateUrl: './submission-form.component.html'
})
export class SubmissionFormComponent implements OnInit {
  active;
  disabled = true;
  submissionForm: FormGroup;
  patient = null;
  requiredError= "this field is required";
  phenotypes = [];

  phenotype$ : Observable<any>;
  phenotypeLoading = false;
  phenotypeInput$ = new Subject<string>();
  submissionId = null;
  
  constructor(private fb: FormBuilder,
    public subService: SubmissionsService,
    private patientService: PatientService,
    private lookupService: LookupService,
    private router: Router,
    private route: ActivatedRoute, 
    private config: NgSelectConfig,
    public toastService: ToastService) {
      this.config.appendTo = 'body';
    }

  ngOnInit(): void {
    this.submissionForm = this.fb.group({
      id: [],
      patient: this.fb.group({
        id:[],
        mrn:[],
        identifier: ['', Validators.required],
        first_name: ['', [Validators.required]],
        last_name: ['', ],
        full_name: [],
        gender: ['unknown', Validators.required],
        date_of_birth: [null],
        phenotypes:[[], Validators.required],
        pedigree: []
      }),
      sequence_file1: [''],
      sequence_file_location1: [],
      sequence_filename1: [],
      sequence_file2: [''],
      sequence_file_location2: [],
      sequence_filename2: [],
      bed_file: [''],
      bed_file_location: [],
      bed_filename: [],
      assembly: ['GRCh38'],
      father_sequence_file1: [''],
      father_sequence_file_location1: [],
      father_sequence_filename1: [],
      father_sequence_file2: [''],
      father_sequence_file_location2: [],
      father_sequence_filename2: [],
      father_bed_file: [''],
      father_bed_file_location: [],
      father_bed_filename: [],
      father_assembly: ['GRCh38'],
      mother_sequence_file1: [''],
      mother_sequence_file_location1: [],
      mother_sequence_filename1: [],
      mother_sequence_file2: [''],
      mother_sequence_file_location2: [],
      mother_sequence_filename2: [],
      mother_bed_file: [''],
      mother_bed_file_location: [],
      mother_bed_filename: [],
      mother_assembly: ['GRCh38'],
      sibling_sequence_file1: [''],
      sibling_sequence_file_location1: [],
      sibling_sequence_filename1: [],
      sibling_sequence_file2: [''],
      sibling_sequence_file_location2: [],
      sibling_sequence_filename2: [],
      sibling_bed_file: [''],
      sibling_bed_file_location: [],
      sibling_bed_filename: [],
      sibling_assembly: ['GRCh38'],
      status: ['draft']
    });
    this.loadPhenotype();
    this.route.params.subscribe(params => {
      this.submissionId = params.id ? params.id != undefined: null;
      if (this.submissionId){
        this.subService.get(this.submissionId).subscribe(res => {
          this.submissionForm.setValue(this.transformSubmission(res));
        });
      }
    });
    
  }

  cancel() {
    this.router.navigate(['/submission']);
  }

  save() { 
    var submission = Object.assign({}, this.submissionForm.value);

    console.log("submission", submission);
    this.subService.addOrUpdate(submission).subscribe(res => {
      this.toastService.show('Saved patient\'s submission', { classname: 'bg-success text-light', delay: 3000 });
      this.submissionForm.setValue(this.transformSubmission(res));
    });
  }

  submit() { 
    var submission = Object.assign({}, this.submissionForm.value);

    console.log("submitting submission", submission);
    this.subService.submit(submission).subscribe(res => {
      this.toastService.show('Submitted patient\'s submission successfully', { classname: 'bg-success text-light', delay: 3000 });
      this.router.navigate(['/submission']);
    });
  }

  back() {
    this.active -= 1;
  }

  next() {
    if (this.active == 1) {
      this.savePatient();
    } else if (this.active == 2) {
      //pass
    }

    this.active += 1;
  }

  onNavChange(changeEvent: NgbNavChangeEvent) {
    this.active += 1;
    if (changeEvent.nextId === 3) {
      changeEvent.preventDefault();
    } 
  }

  get f() { return this.submissionForm.controls }
  get patientForm() { return this.submissionForm.get('patient') }
  get pedigreeForm() { return this.f['patient']['controls']['pedigree'] }

  savePatient () {
    var patient = Object.assign({}, this.f['patient'].value);
    patient['date_of_birth'] = this.toModel(patient['date_of_birth']);
    patient['phenotypes'] = patient['phenotypes'].map(phenotype => {
      let phenotypeObj = { phenotype : { uri: phenotype.class, label:phenotype.label[0] } }
      phenotypeObj.phenotype['id'] = phenotype['id'] ? phenotype['id'] : null;
      return phenotypeObj
    })
    patient.identifier = patient.identifier['identifier'] ? patient.identifier.identifier: patient.identifier;

    delete patient['age']
    if (this.patient) {
      patient['id'] = this.patient.id
    }

    console.log("patient object before updating: ", patient)
    this.patientService.addOrUpdate(patient).subscribe(res => {
      this.patientForm.setValue(this.transformPatient(res));
    });
  }


  loadPhenotype() {
    this.phenotype$ = concat(
        of([]), // default items
        this.phenotypeInput$.pipe(
            distinctUntilChanged(),
            tap(() => this.phenotypeLoading = true),
            switchMap(term => this.lookupService.findEntityByLabelStartsWith(term).pipe(
                map(data => data['result']),
                catchError(() => of([])), // empty list on error
                tap(() => this.phenotypeLoading = false)
            ))
        )
    );
  }


  trackByFn(item: any) {
    return item.class;
  }

  onPhenotypeSelect(event) {
    console.log('phenotype select', this.patientForm['controls'].phenotypes)
  }

  toModel(date: NgbDateStruct | null): string | null {
    return date ? date.year + '-' 
      + (date.month > 9 ? date.month: '0' + date.month) + '-' 
      + (date.day > 9 ? date.day: '0' + date.day) : null;
  }

  isNumber(value: any): value is number {
    return !isNaN(parseInt(value, 10));
  }

  fromModel(value: string): NgbDateStruct | null {
    if (value != null) {
      const dateParts = value.trim().split('-');
      if (dateParts.length === 1 && this.isNumber(dateParts[0])) {
        return {year: parseInt(dateParts[0], 10), month: <any>null, day: <any>null};
      } else if (dateParts.length === 2 && this.isNumber(dateParts[0]) && this.isNumber(dateParts[1])) {
        return {year: parseInt(dateParts[0], 10), month: parseInt(dateParts[1]), day: <any>null};
      } else if (dateParts.length === 3 && this.isNumber(dateParts[0]) && this.isNumber(dateParts[1]) && this.isNumber(dateParts[2])) {
        return {year: parseInt(dateParts[0], 10), month: parseInt(dateParts[1], 10), day: parseInt(dateParts[2], 10)};
      }
    }
    return null;
  }

  onPatientSelect(event){
    this.patientForm.setValue(this.transformPatient(event));
  }

  transformPatient(patient) {
    let obj = Object.assign({}, patient);
    obj['phenotypes'] = obj['phenotypes'].map(phenotype => {
      return { class: phenotype.phenotype.uri, label: [phenotype.phenotype.label], id: phenotype.phenotype.id }
    });
    if (obj['date_of_birth']) {
      obj['date_of_birth'] = this.fromModel(obj['date_of_birth']);
    }
    obj['pedigree'] = {}
    delete obj['age']
    return obj;
  }

  transformSubmission(submission) {
    submission['patient'] = this.transformPatient(submission['patient'])
    submission['sequence_file1'] = ''
    submission['sequence_file2'] = ''
    submission['bed_file'] = ''
    submission['father_sequence_file1'] = ''
    submission['father_sequence_file2'] = ''
    submission['father_bed_file'] = ''
    submission['mother_sequence_file1'] = ''
    submission['mother_sequence_file2'] = ''
    submission['mother_bed_file'] = ''
    submission['sibling_sequence_file1'] = ''
    submission['sibling_sequence_file2'] = ''
    submission['sibling_bed_file'] = ''


    delete submission['is_exome'];
    delete submission['is_paired'];
    delete submission['is_trio'];
    delete submission['date'];
    delete submission['col_uuid'];
    delete submission['error_message'];
    delete submission['created_at'];
    delete submission['updated_at'];
    delete submission['user'];
    return submission;
  }
}
