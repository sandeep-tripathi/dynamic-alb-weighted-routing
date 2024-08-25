# dynamic-alb-weighted-routing
Dynamic ALB Weighted Routing in AWS with combined EC2 Metrics and OIDC Authentication 

Folder Structure:
dynamic-alb-weighted-routing/
│
├── aws_auth.py                  # Although common practice, static credentials are bad practice
├── oidc_boto_authentication.py
├── asg_management.py
├── alb_weighted_routing.py
├── tests/
│   ├── test_alb_weighted_routing.py
│   ├── test_aws_auth.py
│   ├── test_oidc_boto_authentication.py
├── requirements.txt
├── README.md
└── .env

