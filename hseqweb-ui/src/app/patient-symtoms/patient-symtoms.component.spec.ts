import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { PatientSymtomsComponent } from './patient-symtoms.component';

describe('PatientSymtomsComponent', () => {
  let component: PatientSymtomsComponent;
  let fixture: ComponentFixture<PatientSymtomsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ PatientSymtomsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(PatientSymtomsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
