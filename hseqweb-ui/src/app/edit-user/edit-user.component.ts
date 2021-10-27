import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from 'src/auth.service';

@Component({
  selector: 'app-edit-user',
  templateUrl: './edit-user.component.html'
})
export class EditUserComponent implements OnInit {
  user: any = {};
  editUserForm : FormGroup;
  requiredError= "this field is required";
  error={};

  constructor(
    public fb: FormBuilder,
    public authService: AuthService,
    public router: Router) {
  }

  ngOnInit() { 
    this.editUserForm = this.fb.group({
      first_name: ['', ],
      last_name: ['', ],
      organization: ['', ]
    });
        
    this.user = this.authService.getUser().subscribe(data =>{
      this.user = data;
      this.editUserForm.setValue({ 'first_name' : this.user.first_name, 'last_name' : this.user.last_name, 'organization' : this.user.organization });
    })
  }

  registerUser() {
    var user = Object.assign({}, this.editUserForm.value);
    this.error = {};
    this.authService.edit(user).subscribe((res) => {
      if (res) {
        this.editUserForm.reset()
        this.router.navigate(['user']);
      }
    }, err => {
      if (err.status == 400) {
        this.error = err.error;
      }
    });
  }

  get f() { return this.editUserForm.controls }

  cancel(){
    this.router.navigate(['user']);
  }

}
