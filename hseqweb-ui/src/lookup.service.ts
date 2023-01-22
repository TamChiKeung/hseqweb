import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { of } from 'rxjs';
import { _ } from 'underscore';

@Injectable()
export class LookupService {

  options = {
    headers:  new HttpHeaders({
      'Accept': 'application/json'
    })
  };
  
  constructor(private http: HttpClient) { }

  findEntityByLabelStartsWith(term: string) {
    var queryStr = `query=${term}&ontology=hp`;
    return this.http.get(`/api/class/_startwith?${queryStr}`, this.options);
  }

  findEntityByIris(iris:any[], valueset:string) {
    var req;
    if (!valueset) {
      req = {'iri': iris}
    } else {
      req = {'iri': iris, valueset: valueset}
    }
    return this.http.post(`/api/class/_findbyiri`, req, this.options);
  }

}
