import { Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html'
})
export class LoginComponent implements OnInit {
  @ViewChild('captchaRef') captchaRef;
  loginForm: FormGroup;

  recaptcha: string;
  requiredError= "this field is required";
  error="";

  constructor(
    public fb: FormBuilder,
    public authService: AuthService,
    public router: Router) {
      this.recaptcha = '';
  }

  ngOnInit() {     
    if (this.authService.isLoggedIn) {
      this.router.navigate(['user'])
    }

    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required],
      remember: [false, ],
    })
  }

  loginUser() {
    this.error = '';
    let data = Object.assign({}, this.loginForm.value);
    data['recaptcha'] = this.recaptcha
    this.authService.login(data).subscribe(data => {
      this.authService.updateData(data)
      this.router.navigate(['user']);
    }, err => {
      if (err.status == 404) {
        this.error = err.error.error;
      } else if (err.status == 400 && err.error.recaptcha) {
        this.error = err.error.recaptcha[0];
      } 
      this.recaptcha = '';
      this.captchaRef.reset();
    });
  }

  linkToRegister() {
    this.router.navigate(['signup']);
  }

  resolved(captchaResponse: string) {
    this.recaptcha = captchaResponse;
  }

  get f() { return this.loginForm.controls }
}
