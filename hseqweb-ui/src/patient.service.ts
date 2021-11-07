import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class PatientService {

  URL = '/api/patient';
  options = {
    headers:  new HttpHeaders({
      'Accept': 'application/json'
    })
  };

  constructor(private http: HttpClient){ }

  find(): Observable<any>  {
    var url = `${this.URL}`;
    return this.http.get(url, this.options);
  }

  findStartsWith(term, limit) {
    var url = `${this.URL}/startswith?term=${term}&limit=${limit}`;
    return this.http.get(url, this.options);
  }

  get(id) {
    return this.http.get(`${this.URL}/${id}`, this.options);
  }
  
  delete(id) {
    return this.http.delete(`${this.URL}/${id}`, this.options);
  }

  addOrUpdate(data) {
    return this.http.post(this.URL, data);
  }

  updatePedigree(id, data) {
    return this.http.put(`${this.URL}/${id}/pedigree`, data);
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
