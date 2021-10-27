import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AuthGuard } from 'src/auth.guard';
import { ChangePasswordComponent } from './change-password/change-password.component';
import { ContactsComponent } from './contacts/contacts.component';
import { DocumentationComponent } from './documentation/documentation.component';
import { EditUserComponent } from './edit-user/edit-user.component';
import { ListSubmissionComponent } from './list-submission/list-submission.component';
import { LoginComponent } from './login/login.component';
import { SignupComponent } from './signup/signup.component';
import { ValidationRunsComponent } from './validation-runs/validation-runs.component';
import { ViewSubmissionComponent } from './view-submission/view-submission.component';
import { ViewUserComponent } from './view-user/view-user.component';


const routes: Routes = [
  {path: 'validations',component: ValidationRunsComponent},
  {path: 'doc',component: DocumentationComponent},
  {path: 'contacts',component: ContactsComponent},
  {path: 'signup',component: SignupComponent},
  {path: 'login',component: LoginComponent}, 
  {path: 'user',component: ViewUserComponent, canActivate: [AuthGuard]},
  {path: 'user/edit',component: EditUserComponent, canActivate: [AuthGuard]},
  {path: 'user/changepassword',component: ChangePasswordComponent, canActivate: [AuthGuard]},
  {path: 'submission',component: ListSubmissionComponent, canActivate: [AuthGuard]},
  {path: 'submission/:id',component: ViewSubmissionComponent, canActivate: [AuthGuard]}];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
