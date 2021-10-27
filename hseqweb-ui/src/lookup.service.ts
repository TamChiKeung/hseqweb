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

  GENE_VALUESETS = ['NCBIGene']

  constructor(private http: HttpClient) { 
  }

  findValueset() {
    return this.http.get(`/api/valueset`, this.options);
  }

  findEntityByLabelStartsWith(term: string, valueset: string[], pagesize:number) {
    if (term === '' || valueset.length < 1) {
      return of([]);
    }

    var queryStr = `term=${term}`;
    valueset.forEach(function (value) {
      queryStr += "&valueset=" + value;
    });
    if (pagesize) {
      queryStr += "&pagesize=" + pagesize;
    }
    return this.http.get(`/api/entity/_startswith?${queryStr}`, this.options);
  }

  findEntityByIris(iris:any[], valueset:string) {
    var req;
    if (!valueset) {
      req = {'iri': iris}
    } else {
      req = {'iri': iris, valueset: valueset}
    }
    return this.http.post(`/api/entity/_findbyiri`, req, this.options);
  }

}
