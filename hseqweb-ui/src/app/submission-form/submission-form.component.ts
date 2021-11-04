import { NgIf } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { NgbDateStruct, NgbNavChangeEvent } from '@ng-bootstrap/ng-bootstrap';
import { NgbDateISOParserFormatter } from '@ng-bootstrap/ng-bootstrap/datepicker/ngb-date-parser-formatter';
import { NgSelectConfig } from '@ng-select/ng-select';
import { concat, Observable, of, Subject } from 'rxjs';
import { catchError, distinctUntilChanged, map, switchMap, tap } from 'rxjs/operators';
import { LookupService } from 'src/lookup.service';
import { PatientService } from 'src/patient.service';
import { SubmissionsService } from 'src/submission.service';

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
  
  constructor(private fb: FormBuilder,
    public subService: SubmissionsService,
    private patientService: PatientService,
    private lookupService: LookupService,
    private router: Router,
    private config: NgSelectConfig) {
      this.config.appendTo = 'body';
    }

  ngOnInit(): void {
    this.submissionForm = this.fb.group({
      patient: this.fb.group({
        id:[],
        mrn:[],
        identifier: ['', Validators.required],
        first_name: ['', [Validators.required]],
        last_name: ['', ],
        full_name: [],
        gender: ['unknown', Validators.required],
        date_of_birth: [null],
        age:[],
        phenotypes:[[], Validators.required]
      })
    });
    this.loadPhenotype();
  }

  cancel() {
    this.router.navigate(['/submission']);
  }

  submit() {
  }

  back() {
    this.active -= 1;
  }

  next() {
    if (this.active == 1) {
      this.savePatient()
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

  savePatient () {
    var patient = Object.assign({}, this.f['patient'].value);
    patient['date_of_birth'] = this.toModel(patient['date_of_birth']);
    patient['phenotypes'] = patient['phenotypes'].map(phenotype => {
      let phenotypeObj = { phenotype : { uri: phenotype.class, label:phenotype.label[0] } }
      phenotypeObj.phenotype['id'] = phenotype['id'] ? phenotype['id'] : null;
      return phenotypeObj
    })
    patient.identifier = !(patient.identifier instanceof String) ? patient.identifier.identifier: patient.identifier;

    delete patient['age']
    if (this.patient) {
      patient['id'] = this.patient.id
    }

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
    return obj;
  }
}
