import { Injectable } from "@angular/core";
import { HttpInterceptor, HttpRequest, HttpHandler } from "@angular/common/http";
import { AuthService } from "./auth.service";

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
    constructor(private authService: AuthService) { }

    intercept(req: HttpRequest<any>, next: HttpHandler) {
        if (req.url.includes('api/user/_login') || req.url.includes('api/user/_register')) {
            return next.handle(req);
        }

        const authToken = this.authService.getToken();
        if (authToken) {
            req = req.clone({
                setHeaders: {
                    Authorization: "Token " + authToken
                }
            });
        }
        return next.handle(req);
    }
}