CREATE MIGRATION m1jnkl2tuyxeu45jnde6linjr2h4yfg6g4mvl4yw2cuca674qb7dwq
    ONTO initial
{
  CREATE FUTURE simple_scoping;
  CREATE TYPE default::Company {
      CREATE PROPERTY employees: std::int32;
      CREATE PROPERTY founding_year: std::int32;
      CREATE PROPERTY headquarters: std::str;
      CREATE PROPERTY industry: std::str;
      CREATE PROPERTY market_cap: std::float64;
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE PROPERTY revenue: std::float64;
      CREATE REQUIRED PROPERTY stock_ticker: std::str {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  CREATE TYPE default::Acquisition {
      CREATE LINK acquired: default::Company;
      CREATE LINK acquirer: default::Company;
      CREATE PROPERTY amount: std::float64;
      CREATE PROPERTY date: std::cal::local_date;
  };
  CREATE TYPE default::Collaboration {
      CREATE MULTI LINK participants: default::Company;
      CREATE PROPERTY end_date: std::cal::local_date;
      CREATE PROPERTY focus: std::str;
      CREATE PROPERTY funding: std::float64;
      CREATE PROPERTY name: std::str;
      CREATE PROPERTY start_date: std::cal::local_date;
  };
  CREATE TYPE default::StockPrice {
      CREATE REQUIRED LINK company: default::Company;
      CREATE REQUIRED PROPERTY date: std::cal::local_date;
      CREATE CONSTRAINT std::exclusive ON ((.date, .company));
      CREATE REQUIRED PROPERTY close: std::float64;
      CREATE PROPERTY high: std::float64;
      CREATE PROPERTY low: std::float64;
      CREATE PROPERTY open: std::float64;
      CREATE PROPERTY volume: std::int64;
  };
  CREATE TYPE default::Product {
      CREATE LINK manufacturer: default::Company;
      CREATE PROPERTY approval_date: std::cal::local_date;
      CREATE REQUIRED PROPERTY name: std::str;
      CREATE PROPERTY revenue: std::float64;
      CREATE PROPERTY type: std::str;
  };
  CREATE TYPE default::NewsArticle {
      CREATE MULTI LINK mentions_companies: default::Company;
      CREATE MULTI LINK mentions_products: default::Product;
      CREATE PROPERTY author: std::str;
      CREATE PROPERTY category: std::str;
      CREATE PROPERTY content: std::str;
      CREATE PROPERTY metadata: std::json;
      CREATE PROPERTY publication_date: std::datetime;
      CREATE PROPERTY sentiment_score: std::float32;
      CREATE PROPERTY source: std::str;
      CREATE PROPERTY summary: std::str;
      CREATE PROPERTY tags: array<std::str>;
      CREATE REQUIRED PROPERTY title: std::str;
      CREATE REQUIRED PROPERTY url: std::str {
          CREATE CONSTRAINT std::exclusive;
      };
  };
};
