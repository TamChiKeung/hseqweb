import { Component, Input, OnInit, SimpleChange } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { NgbDateStruct, NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { PatientService } from 'src/patient.service';

@Component({
  selector: 'app-patient-pedigree',
  templateUrl: './patient-pedigree.component.html'
})
export class PatientPedigreeComponent implements OnInit {
  @Input() indexPatient = null;
  patient = null;
  pedigreeForm: FormGroup;
  
  constructor(private fb: FormBuilder,
    private patientService: PatientService,
    private modalService: NgbModal) { }

  ngOnInit(): void {
    this.pedigreeForm = this.fb.group({
      id:[],
      father: this.patientShortFormGroup('male'),
      mother: this.patientShortFormGroup('female'),
      sibling: this.patientShortFormGroup('unknown')
    })
  }

  ngOnChanges(change: SimpleChange) {
    if(change && change['indexPatient'] && this.indexPatient && this.indexPatient.id) {
      this.patientService.get(this.indexPatient.id).subscribe(res => {
        this.patient = res;
        console.log(res, this.patient['pedigree'])
        if (this.patient['pedigree']) {
          this.pedigreeForm.setValue(this.fromPedigreeModel(this.patient['pedigree']));
        }
      });
    }
  }

  patientShortFormGroup(gender) {
    return this.fb.group({
              id:[],
              mrn:[],
              identifier: ['', Validators.required],
              first_name: ['', [Validators.required]],
              last_name: ['', ],
              full_name: [],
              gender: [gender, Validators.required],
              date_of_birth: [null],
              phenotypes: []
            });
  }

  get f() { return this.pedigreeForm.controls }
  get fatherForm() { return this.pedigreeForm.get('father') }
  get motherForm() { return this.pedigreeForm.get('mother') }
  get siblingForm() { return this.pedigreeForm.get('sibling') }

  onFatherSelect(event) {
    this.fatherForm.setValue(this.transformPatient(event));
  }

  onMotherSelect(event) {
    this.motherForm.setValue(this.transformPatient(event));
  }

  onSiblingSelect(event) {
    this.siblingForm.setValue(this.transformPatient(event));
  }

  save(){
    var pedigree = Object.assign({}, this.f.value);
    let father =  this.toPatientModel(Object.assign({}, this.fatherForm.value));
    if (father['identifier'] != '') {
      pedigree['father'] = this.toPatientModel(father);
    }


    let mother =  this.toPatientModel(Object.assign({}, this.motherForm.value));  
    if (mother['identifier'] != '') {
      pedigree['mother'] = this.toPatientModel(mother);
    }

    let sibling =  this.toPatientModel(Object.assign({}, this.siblingForm.value));  
    if (sibling['identifier'] != '') {
      if (sibling['gender'] == 'male') {
        pedigree['brother'] = this.toPatientModel(sibling);
        pedigree['sister'] = null;
      } else if (sibling['gender'] == 'female') {
        pedigree['sister'] = this.toPatientModel(sibling);
        pedigree['brother'] = null;
      }
    }

    var data = {'id': this.patient.id, 'pedigree': pedigree}
    this.patientService.updatePedigree(this.patient.id, data).subscribe(res => {
      this.patient = res;
      this.pedigreeForm.setValue(this.fromPedigreeModel(this.patient['pedigree']));
    }); 
  }

  toPatientModel(patient) {
    patient['date_of_birth'] = this.toModel(patient['date_of_birth']);
    patient.identifier = !(typeof patient.identifier === 'string') ? patient.identifier.identifier: patient.identifier;
    delete patient['age']
    return patient;
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


  transformPatient(patient) {
    let obj = Object.assign({}, patient);
    if (obj['date_of_birth']) {
      obj['date_of_birth'] = this.fromModel(obj['date_of_birth']);
    }
    return obj;
  }

  fromPedigreeModel(pedigree) {
    pedigree = Object.assign({}, pedigree);
    pedigree['father'] = pedigree['father'] ? this.transformPatient(pedigree['father']): null;
    pedigree['mother'] = pedigree['mother'] ? this.transformPatient(pedigree['mother']): null;

    pedigree['sibling'] = this.siblingForm.value;
    let sibling= null;
    if (pedigree['brother']) {
      sibling = this.transformPatient(pedigree['brother']);
      if (sibling && sibling['identifier']) {
        pedigree['sibling'] = sibling
      }
    } 
    delete pedigree['brother']; 

    if (pedigree['sister']) {
      sibling = this.transformPatient(pedigree['sister']);
      if (sibling && sibling['identifier']) {
        pedigree['sibling'] = sibling
      }
    } 
    
    delete pedigree['sister'];
    return pedigree;
  }

  open(content) {
    this.modalService.open(content, {size: 'lg'});
  }

  cancelModal(modal){
    modal.dismiss('cancel click');
  }
}
