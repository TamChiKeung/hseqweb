import { Component, OnInit } from '@angular/core';
import { NgbAlertConfig } from '@ng-bootstrap/ng-bootstrap';
import { SubmissionsService } from 'src/submission.service';

@Component({
  selector: 'app-list-submission',
  templateUrl: './list-submission.component.html'
})
export class ListSubmissionComponent implements OnInit {
  submissions: any = [];

  page = 1;
  previousPage = 1;
  pageSize = 10;
  collectionSize = 0;

  constructor(public subService: SubmissionsService,
    private alertConfig: NgbAlertConfig) { 
      alertConfig.type = 'secondary';
  }

  ngOnInit(): void {
    this.page = 1;
    this.previousPage = 1;
    this.pageSize = 10;
    this.findSubmissions();
    
  }

  loadPage(page: number) {
    if (page !== this.previousPage) {
      this.previousPage = page;
      this.findSubmissions()
    }
  }

  findSubmissions() {
    var offset = 0
    if (this.page > 1) {
      offset = this.pageSize * (this.page - 1)
    }
    
    this.subService.find(this.pageSize, offset).subscribe(data =>{
      this.submissions = data.result;
      this.collectionSize = data.total;
    })
  }

}
