import { Injectable } from '@angular/core';
import { User } from './model/user';
import { Observable, throwError } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { HttpClient, HttpHeaders, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { CookieService } from 'ngx-cookie-service';
import { UserChangePassword } from './model/user-change-password';

@Injectable()
export class AuthService {
  URL = '/api/user';c
  headers = new HttpHeaders().set('Content-Type', 'application/json');
  token: string;
  token_expires: Date;
  username: string;
  errors: any = [];
 
  constructor(private http: HttpClient,
    private cookieService: CookieService,
    public router: Router) { }
 
  // Uses http.post() to get an auth token from djangorestframework-jwt endpoint
  login(user) {
    return this.http.post(`${this.URL}/_login`, user);
  }
  getToken() {
    return this.cookieService.get('token');
  }

  get isLoggedIn(): boolean {
    let authToken = this.cookieService.get('token');
    return (authToken) ? true : false;
  }

  logout() {
    let api = `${this.URL}/_logout`;
    return this.http.get(api, { headers: this.headers }).pipe(catchError(this.handleError));
  }

  clearCache(){
    let removeToken = this.cookieService.delete('token');
    if (removeToken == null) {
      this.cookieService.delete('username');
    }
  }

  getUser(): Observable<any> {
    let api = `${this.URL}`;
    return this.http.get(api, { headers: this.headers }).pipe(catchError(this.handleError))
  }

  signUp(user: User): Observable<any> {
    let api = `${this.URL}/_register`;
    return this.http.post(api, user);
  }

  changePassword(user: UserChangePassword): Observable<any> {
    let api = `${this.URL}/_changepassword`;
    return this.http.put(api, user);
  }
  
  edit(user: any): Observable<any> {
    let api = `${this.URL}/_edit`;
    return this.http.put(api, user);
  }

  updateData(data) {
    this.cookieService.set('token', data['token'])
    this.cookieService.set('username', data['username'])
  }

  getUsername() {
    return this.cookieService.get('username');
  }

  private handleError(error: HttpErrorResponse) {
    let msg = '';
    if (error.error instanceof ErrorEvent) {
      // client-side error
      msg = error.error.message;
    } else {
      // server-side error
      msg = `Error Code: ${error.status}\nMessage: ${error.message}`;
    }
    return throwError(msg);
  }
 
}
