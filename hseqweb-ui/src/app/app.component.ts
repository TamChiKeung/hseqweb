import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from 'src/auth.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  constructor(public authService:AuthService,
    public router: Router) { 
  }

logout(){
  this.authService.logout().subscribe(data => {
    this.authService.clearCache();
    this.router.navigate(['login']);
  });
}

userProfile() {
  this.router.navigate(['user']);
}

openInNewTab(url: string) {
  window.open(url, "_blank");
}
}
