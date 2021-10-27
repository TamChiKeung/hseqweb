import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { SubmissionsService } from 'src/submission.service';

@Component({
  selector: 'app-view-submission',
  templateUrl: './view-submission.component.html',
  providers:[NgbModal]
})
export class ViewSubmissionComponent implements OnInit {
  submission : any = null;

  constructor(public subService: SubmissionsService,
    private modalService: NgbModal,
    private route: ActivatedRoute,
    public router: Router) { }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      this.subService.get(params.id).subscribe(data =>{
        this.submission = data;
      });
    });
  }

  onDelete(id) {
    this.subService.delete(id).subscribe(data =>{
      this.router.navigate(['submission']);
    });
  }
  
  open(content) {
    this.modalService.open(content);
  }

  close() {}

}