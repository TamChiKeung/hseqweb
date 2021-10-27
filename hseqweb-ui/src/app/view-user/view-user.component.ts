import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from 'src/auth.service';

@Component({
  selector: 'app-view-user',
  templateUrl: './view-user.component.html'
})
export class ViewUserComponent implements OnInit {
  user: any = {};

  constructor(public authService: AuthService,
    private route: ActivatedRoute) {
    this.user = this.authService.getUser().subscribe(data =>{
      this.user = data;
    })
  }

  ngOnInit(): void {
  }

}
