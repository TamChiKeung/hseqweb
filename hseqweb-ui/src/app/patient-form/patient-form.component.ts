import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgbCalendarGregorian, NgbDate, NgbDateStruct } from '@ng-bootstrap/ng-bootstrap';
import { merge, Observable, of, Subject } from 'rxjs';
import { catchError, debounceTime, distinctUntilChanged, switchMap, tap } from 'rxjs/operators';
import { Patient } from 'src/model/patient';
import { PatientService } from 'src/patient.service';


@Component({
  selector: 'app-patient-form',
  templateUrl: './patient-form.component.html'
})
export class PatientFormComponent implements OnInit {
  @Input() patientForm: FormGroup;
  @Output() patientSelectEvent = new EventEmitter<any>();

  error = {};
  requiredError= "this field is required";
  model: NgbDateStruct;
  today: NgbDate

  focus$ = new Subject<string>();
  searchFailed = false;

  genders = {
    MALE: 'male',
    FEMALE: 'female',
    UNKNOWN: 'unknown'
  }

  formatter = (x) => { 
    return x.identifier ? x.identifier : '';
  }

  search = (text$: Observable<string>) => {
    const debouncedText$ = text$.pipe(debounceTime(500), distinctUntilChanged());
    const inputFocus$ = this.focus$;
    return merge(debouncedText$, inputFocus$).pipe(
      switchMap(term =>
        this.findPatient(term).pipe(
          tap(() => this.searchFailed = false),
          catchError(() => {
            this.searchFailed = true;
            return of([]);
          }))
    ));
  }

  constructor(private fb: FormBuilder,
    private patientService: PatientService) { 
    this.today = (new NgbCalendarGregorian()).getToday();
  }

  ngOnInit(): void {
    
  }

  get f() { return this.patientForm.controls }

  keys = Object.keys;

  onPatientSelect(event){
    this.patientSelectEvent.emit(event.item);
  }

  findPatient(term) {
    return this.patientService.findStartsWith(term, 20);
  }
}
