import { Component, OnInit } from '@angular/core';
import { SubmissionsService } from 'src/submission.service';

@Component({
  selector: 'app-validation-runs',
  templateUrl: './validation-runs.component.html'
})
export class ValidationRunsComponent implements OnInit {
  validations: any = {};

  constructor(public subService: SubmissionsService) {
  }

  ngOnInit(): void {
    this.subService.getValidationRuns().subscribe(data =>{
      this.validations = data;
    })
  }

}
