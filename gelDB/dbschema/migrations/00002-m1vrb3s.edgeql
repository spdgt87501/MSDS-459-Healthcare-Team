CREATE MIGRATION m1vrb3s7b255lzglllbssfbswprcqb2xp2xhycqo37kqqogj4taq2a
    ONTO m1jnkl2tuyxeu45jnde6linjr2h4yfg6g4mvl4yw2cuca674qb7dwq
{
  ALTER TYPE default::Acquisition {
      DROP LINK acquirer;
  };
  ALTER TYPE default::Acquisition {
      DROP PROPERTY amount;
  };
  ALTER TYPE default::Acquisition RENAME TO default::Relation;
  ALTER TYPE default::Collaboration {
      DROP LINK participants;
  };
  ALTER TYPE default::Collaboration {
      DROP PROPERTY end_date;
  };
  ALTER TYPE default::Collaboration {
      DROP PROPERTY funding;
  };
  ALTER TYPE default::Collaboration {
      DROP PROPERTY start_date;
  };
  ALTER TYPE default::Collaboration RENAME TO default::Entity;
  ALTER TYPE default::Entity {
      ALTER PROPERTY focus {
          RENAME TO label;
      };
      ALTER PROPERTY name {
          SET REQUIRED USING (<std::str>'UNKNOWN');
      };
  };
  ALTER TYPE default::Relation {
      ALTER LINK acquired {
          RENAME TO company;
      };
  };
  ALTER TYPE default::Relation {
      CREATE REQUIRED PROPERTY object: std::str {
          SET REQUIRED USING (<std::str>'UNKNOWN_OBJECT');
      };
      CREATE REQUIRED PROPERTY relation: std::str {
          SET REQUIRED USING (<std::str>'UNKNOWN_RELATION');
      };
      CREATE PROPERTY sentence: std::str;
      CREATE REQUIRED PROPERTY subject: std::str {
          SET REQUIRED USING (<std::str>'UNKNOWN_SUBJECT');
      };
      CREATE PROPERTY url: std::str;
  };
};
