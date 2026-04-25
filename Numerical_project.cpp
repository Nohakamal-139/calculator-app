#include "exprtk.hpp"
#include <iostream>
#include <cmath>
#include <vector>
#include <functional>
#include <string>

using namespace std;

// --- دالة Bisection مطورة لتسجيل الخطوات ---
void bisection(function<double(double)> f, double a, double b, double tol) {
    if (f(a) * f(b) >= 0) { cout << "ERROR: No root in interval"; return; }
    double c;
    int iter = 0;
    while ((b - a) >= tol && iter < 100) {
        c = (a + b) / 2.0;
        // بنطبع: رقم الخطوة | قيمة c | قيمة الدالة (عشان الجدول في بايثون)
        cout << iter << "," << c << "," << f(c) << "\n";
        if (abs(f(c)) < 1e-12) break;
        else if (f(c) * f(a) < 0) b = c;
        else a = c;
        iter++;
    }
}

// --- دالة Newton مطورة لتسجيل الخطوات ---
void newton(function<double(double)> f, double x0, double tol) {
    double x = x0;
    auto fPrime = [f](double x) {
        double h = 1e-8;
        return (f(x + h) - f(x)) / h;
        };
    for (int i = 0; i < 50; i++) {
        double fx = f(x);
        double fpx = fPrime(x);
        cout << i << "," << x << "," << fx << "\n"; // تسجيل الخطوة
        if (abs(fpx) < 1e-12) break;
        double xNew = x - fx / fpx;
        if (abs(xNew - x) < tol) {
            cout << i + 1 << "," << xNew << "," << f(xNew) << "\n";
            break;
        }
        x = xNew;
    }
}

// --- دالة Gauss-Seidel مطورة ---
void solveGaussSeidel(int n, vector<double> flatA, vector<double> B) {
    vector<double> x(n, 0.0);
    for (int iter = 0; iter < 50; iter++) {
        cout << iter << ",";
        for (int i = 0; i < n; i++) {
            double sum = 0;
            for (int j = 0; j < n; j++) {
                if (j != i) sum += flatA[i * n + j] * x[j];
            }
            x[i] = (B[i] - sum) / flatA[i * n + i];
            cout << x[i] << (i == n - 1 ? "" : " "); // طباعة قيم x1 x2 x3..
        }
        cout << "\n";
    }
}

int main(int argc, char* argv[]) {
    if (argc < 2) return 1;
    int choice = stoi(argv[1]);

    if (choice == 1 || choice == 2) {
        string funcStr = argv[2];
        exprtk::symbol_table<double> symbol_table;
        double x_var;
        symbol_table.add_variable("x", x_var);
        symbol_table.add_constants();
        exprtk::expression<double> expression;
        expression.register_symbol_table(symbol_table);
        exprtk::parser<double> parser;
        parser.compile(funcStr, expression);
        auto f = [&](double val) { x_var = val; return expression.value(); };

        if (choice == 1) bisection(f, stod(argv[3]), stod(argv[4]), 1e-6);
        else newton(f, stod(argv[3]), 1e-6);
    }
    else if (choice == 3) {
        int n = stoi(argv[2]);
        vector<double> A, B;
        int idx = 3;
        for (int i = 0; i < n * n; i++) A.push_back(stod(argv[idx++]));
        for (int i = 0; i < n; i++) B.push_back(stod(argv[idx++]));
        solveGaussSeidel(n, A, B);
    }
    return 0;
}