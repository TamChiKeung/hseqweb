import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/auth.service';
import { MustMatch } from 'src/must-match';

@Component({
  selector: 'app-change-password',
  templateUrl: './change-password.component.html'
})
export class ChangePasswordComponent implements OnInit {
  changePwdForm : FormGroup;
  requiredError= "this field is required";
  error="";

  constructor(
    public fb: FormBuilder,
    public authService: AuthService,
    public router: Router) {
  }

  ngOnInit() { 
    this.changePwdForm = this.fb.group({
      old_password: ['', [Validators.required, Validators.minLength(6)]],
      new_password: ['', [Validators.required, Validators.minLength(6)]],
      new_confirm_password: ['', Validators.required]
    }, {
      validator: MustMatch('new_password', 'new_confirm_password')
    });
  }

  changePassword() {
    var user = Object.assign({}, this.changePwdForm.value);
    delete user['new_confirm_password'];
    this.error = "";

    this.authService.changePassword(user).subscribe((res) => {
      this.changePwdForm.reset()
      this.router.navigate(['user']);
    }, err => {
      if (err.status == 400) {
        this.error = err.error.error;
      }
    });
  }

  get f() { return this.changePwdForm.controls }
  
  cancel(){
    this.router.navigate(['user']);
  }

}
