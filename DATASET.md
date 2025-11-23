## Overview

## https://www.kaggle.com/datasets/blastchar/telco-customer-churn/data

The Telco Customer Churn dataset contains customer-level information from a telecommunications company. Each row represents a customer and includes demographic details, service subscriptions, billing information, and whether the customer churned.

This dataset is widely used for churn prediction, classification tasks, and exploratory data analysis.

## Dataset Size

* Rows: 7,043
* Columns: 21

| Sütun Adı (TR) / Column Name (EN) | Unique Count | Values (Only for 2-category & 3-category features)         | Açıklama (Türkçe & English)                                                                        |
| ----------------------------------- | ------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| **customerID**                | 7043         | —                                                         | **TR:** Müşteri ID’si (benzersiz). **EN:** Unique customer identifier.                  |
| **gender**                    | 2            | Male, Female                                               | **TR:** Müşterinin cinsiyeti. **EN:** Customer’s gender.                                |
| **SeniorCitizen**             | 2            | 0, 1                                                       | **TR:** Yaşlı müşteri (1=Evet). **EN:** Senior citizen indicator (1=Yes).              |
| **Partner**                   | 2            | Yes, No                                                    | **TR:** Partneri var mı? **EN:** Whether the customer has a partner.                      |
| **Dependents**                | 2            | Yes, No                                                    | **TR:** Bakmakla yükümlü olduğu kişi var mı? **EN:** Customer has dependents.        |
| **tenure**                    | 73           | —                                                         | **TR:** Şirkette kalınan ay sayısı. **EN:** Number of months the customer stayed.      |
| **PhoneService**              | 2            | Yes, No                                                    | **TR:** Telefon hizmeti var mı? **EN:** Whether phone service is active.                  |
| **MultipleLines**             | 3            | Yes, No, No phone service                                  | **TR:** Birden fazla telefon hattı kullanım durumu. **EN:** Use of multiple phone lines. |
| **InternetService**           | 3            | DSL, Fiber optic, No                                       | **TR:** İnternet hizmeti türü. **EN:** Type of internet service.                        |
| **OnlineSecurity**            | 3            | Yes, No, No internet service                               | **TR:** Online güvenlik paketi. **EN:** Online security add-on.                           |
| **OnlineBackup**              | 3            | Yes, No, No internet service                               | **TR:** Online yedekleme hizmeti. **EN:** Online backup service.                           |
| **DeviceProtection**          | 3            | Yes, No, No internet service                               | **TR:** Cihaz koruma paketi. **EN:** Device protection plan.                               |
| **TechSupport**               | 3            | Yes, No, No internet service                               | **TR:** Teknik destek hizmeti. **EN:** Technical support availability.                     |
| **StreamingTV**               | 3            | Yes, No, No internet service                               | **TR:** TV yayın hizmeti. **EN:** Streaming TV service.                                   |
| **StreamingMovies**           | 3            | Yes, No, No internet service                               | **TR:** Film yayın servisi. **EN:** Streaming movies service.                             |
| **Contract**                  | 3            | Month-to-month, One year, Two year                         | **TR:** Sözleşme türü. **EN:** Type of contract.                                       |
| **PaperlessBilling**          | 2            | Yes, No                                                    | **TR:** Kağıtsız fatura kullanımı. **EN:** Paperless billing usage.                   |
| **PaymentMethod**             | 4            | Credit card, Bank transfer, Electronic check, Mailed check | **TR:** Ödeme yöntemi. **EN:** Customer’s payment method.                               |
| **MonthlyCharges**            | 1585         | —                                                         | **TR:** Aylık ücret. **EN:** Monthly charges billed.                                     |
| **TotalCharges**              | 6531         | —                                                         | **TR:** Toplam ücret. **EN:** Total amount billed.                                        |
| **Churn**                     | 2            | Yes, No                                                    | **TR:** Müşteri kaybı. **EN:** Whether the customer churned (target variable).          |
