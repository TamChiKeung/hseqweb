import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ContactsComponent } from './contacts/contacts.component';
import { DocumentationComponent } from './documentation/documentation.component';
import { SignupComponent } from './signup/signup.component';
import { LoginComponent } from './login/login.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { MDBBootstrapModule } from 'angular-bootstrap-md';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { RecaptchaModule, RecaptchaSettings, RECAPTCHA_SETTINGS } from 'ng-recaptcha';
import { AuthService } from 'src/auth.service';
import { AuthInterceptor } from 'src/auth.interceptor';
import { AuthGuard } from 'src/auth.guard';
import { CookieService } from 'ngx-cookie-service';
import { ViewUserComponent } from './view-user/view-user.component';
import { ChangePasswordComponent } from './change-password/change-password.component';
import { EditUserComponent } from './edit-user/edit-user.component';
import { ValidationRunsComponent } from './validation-runs/validation-runs.component';
import { SubmissionsService } from 'src/submission.service';
import { LookupService } from 'src/lookup.service';
import { FileSizePipe } from 'src/filesize.pipe';
import { ListSubmissionComponent } from './list-submission/list-submission.component';
import { ViewSubmissionComponent } from './view-submission/view-submission.component';

@NgModule({
  declarations: [
    AppComponent,
    ContactsComponent,
    DocumentationComponent,
    SignupComponent,
    LoginComponent,
    ViewUserComponent,
    ChangePasswordComponent,
    EditUserComponent,
    ValidationRunsComponent,
    FileSizePipe,
    ListSubmissionComponent,
    ViewSubmissionComponent
  ],
  imports: [
    BrowserModule,
    RecaptchaModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    NgbModule,
    MDBBootstrapModule.forRoot(),
    AppRoutingModule
  ],
  providers: [
    {
      provide: RECAPTCHA_SETTINGS,
      useValue: { siteKey: "6LefajoUAAAAAOAWkZnaz-M2lgJOIR9OF5sylXmm" } as RecaptchaSettings,
    },
    CookieService,
    AuthService,
    SubmissionsService,
    LookupService,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    },
    AuthGuard, 
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
