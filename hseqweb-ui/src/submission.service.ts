import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class SubmissionsService {

  URL = '/api/submission';
  options = {
    headers:  new HttpHeaders({
      'Accept': 'application/json'
    })
  };

  constructor(private http: HttpClient){ }

  find(limit:number, offset:number): Observable<any>  {
    var url = `${this.URL}?limit=${limit}&offset=${offset}`;
    return this.http.get(url, this.options);
  }

  get(id) {
    return this.http.get(`${this.URL}/${id}`, this.options);
  }
  
  delete(id) {
    return this.http.delete(`${this.URL}/${id}`, this.options);
  }

  
//   upload(formData){
//     return this.http.post<any>(this.URL + '/_upload', formData, {  
//        reportProgress: true,  
//        observe: 'events'  
//     });  
//  }

  getValidationRuns() {
    return this.http.get(`/api/validationrun`, this.options);
  }
}
