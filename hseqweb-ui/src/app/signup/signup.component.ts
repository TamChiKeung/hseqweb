import { Component, OnInit, ViewChild } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/auth.service';
import { MustMatch } from 'src/must-match';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html'
})
export class SignupComponent implements OnInit {
  @ViewChild('captchaRef') captchaRef;

  registerForm : FormGroup;
  recaptcha: string;
  requiredError= "this field is required";
  error={};

  constructor(
    public fb: FormBuilder,
    public authService: AuthService,
    public router: Router) {
      this.recaptcha = null;
  }

  ngOnInit() { 
    this.registerForm = this.fb.group({
      username: ['', Validators.required],
      email: ['', [Validators.required, Validators.email,Validators.pattern('^[a-z0-9._%+-]+@[a-z0-9.-]+\\.[a-z]{2,4}$')]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', Validators.required]
    }, {
      validator: MustMatch('password', 'confirmPassword')
    });
        
    if (this.authService.isLoggedIn) {
      this.router.navigate(['user'])
    }
  }

  registerUser() {
    var user = Object.assign({}, this.registerForm.value);
    user['recaptcha'] = this.recaptcha
    delete user['confirmPassword'];
    this.error = {};

    this.authService.signUp(user).subscribe((res) => {
      if (res) {
        this.registerForm.reset()
        this.router.navigate(['login']);
      }
    }, err => {
      if (err.status == 400) {
        this.error = err.error;
      } else if (err.status == 400 && err.error.recaptcha) {
        this.error = err.error.recaptcha[0];
      } 
      this.recaptcha = '';
      this.captchaRef.reset();
    });
  }

  get f() { return this.registerForm.controls }

  resolved(captchaResponse: string) {
    this.recaptcha = captchaResponse;
  }

}
