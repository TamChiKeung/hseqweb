import { PatientPedigree } from "./patient-pedigree";

export class Patient {
    id: String;
    identifier: String;
    mrn: String;
    first_name: String;
    last_name: String;
    gender: String;
    date_of_birth: String;
    pedigree: PatientPedigree;
    phentypes: any[];
}   