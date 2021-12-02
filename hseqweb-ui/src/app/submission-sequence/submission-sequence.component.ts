import { Component, Input, OnInit, SimpleChange } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { PatientService } from 'src/patient.service';
import * as tus from "tus-js-client";

@Component({
  selector: 'app-submission-sequence',
  templateUrl: './submission-sequence.component.html'
})
export class SubmissionSequenceComponent implements OnInit {
  @Input() indexPatient = null;
  @Input() submissionForm: FormGroup;
  patient = null;

  endpoint = '/api/tus_upload/';
  chunkSize = 5242880;

  assemblies = {
    GRCh38: 'GRCh38 (hg38)',
    GRCh37: 'GRCh37 (hg19)'
  }

  constructor(private patientService: PatientService) { }

  ngOnInit(): void {
  }

  get f() { return this.submissionForm.controls }

  ngOnChanges(change: SimpleChange) {
    if(change && change['indexPatient'] && this.indexPatient && this.indexPatient.id) {
      this.patientService.get(this.indexPatient.id).subscribe(res => {
        this.patient = res;
        console.log(res, this.patient['pedigree'])
      });
    }
  }

  keys = Object.keys;
}
