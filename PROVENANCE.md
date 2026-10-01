# Provided code provenance

`domain.py` retains the completed Configuration, ConfigurationBounds, Path and
Obstacle classes from the course's Week 4 V10 release. No prior student answer
or installed previous-week package is required.

Source: CURRENT_2026_2/01_weekly_packages/week_04/release/v10_public_20260925/starter/src/ap_week04_scene_data/domain.py
Source SHA-256: 66b3b6162da31e7028224717db2972bef0b4c61000ce7737947a2e6e626e598e

The API retains `Configuration.dimension` as a property and `Path.length()` as
a method. Unneeded request, result, scene and timing classes were omitted.
The supplied length helper is revised to reject unrepresentable arithmetic.
The local Obstacle guard converts radius-conversion overflow into the same
PlanningModelError used for its other invalid inputs. Earlier weeks are unchanged.
Week 5 sampling, signed point/disk clearance, absolute turning, margins and
plain SVG drawing are original course support. Students use these calculations
and do not implement collision geometry or a planning algorithm.

`sample_path` permits at most 10,000 points and checks segment lengths and capacity
before allocation. Nonfinite arithmetic raises PlanningModelError through the
evaluation support. This finite sampled check is not physical-safety evidence.
