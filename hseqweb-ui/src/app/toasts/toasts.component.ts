import { Component, OnInit, TemplateRef } from '@angular/core';
import { ToastService } from 'src/toast-service';

@Component({
  selector: 'app-toasts',
  templateUrl: './toasts.component.html',
  host: {'[class.ngb-toasts]': 'true'}
})
export class ToastsComponent implements OnInit {

  constructor(public toastService: ToastService) {}
  
  ngOnInit(): void {
  }

  isTemplate(toast) { return toast.textOrTpl instanceof TemplateRef; }

}
