import { Component } from '@angular/core';
import { FormGroup, FormBuilder, Validators } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})

export class AppComponent {
  loginForm: FormGroup;
  res!: any;
  user!: any;
  //isLoggedIn: boolean = false;
  constructor(private http: HttpClient, private fb: FormBuilder) {
    this.loginForm = this.fb.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });
    //console.log(this.isLoggedIn);
  } // Injecting HTTPCLIENT MODULE INTO COMPONENT

  post() { // post function
    this.http.post('http://localhost:8000/api/create_user',
     {
      username: this.loginForm.value['username'],
      password: this.loginForm.value['password']
     }, { withCredentials: true }).subscribe((response: any) => { // callback 
      this.res = response['info'];
      const new_token = response['info'];
      localStorage.setItem('token', new_token)
      console.log(this.res);
    });


    //console.log(this.isLoggedIn);
    /*
      event emmitter
      listens for changes to var is logged in  {

      }
    
    */
  }

  

  get() {
    const token = localStorage.getItem('token');
    const head = new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + token
    });

    this.http.get('http://localhost:8000/api/users/me/', { headers: head }).subscribe((data: any) => {
      this.user = data;
      console.log(data);
    });
  }
}