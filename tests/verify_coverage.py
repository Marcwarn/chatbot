"""
Test coverage verification
Ensures critical code paths have adequate test coverage
"""
import sys
import argparse
import xml.etree.ElementTree as ET
import os

def verify_coverage(min_coverage=80):
    """Verify test coverage meets minimum threshold"""

    coverage_file = "coverage.xml"

    if not os.path.exists(coverage_file):
        print(f"❌ Coverage file not found: {coverage_file}")
        print("Run pytest with --cov flag first")
        return 1

    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()

        # Get overall coverage
        coverage = float(root.attrib.get('line-rate', 0)) * 100

        print(f"\n📊 Test Coverage Report")
        print("=" * 50)
        print(f"Overall Coverage: {coverage:.2f}%")
        print(f"Minimum Required: {min_coverage}%")

        if coverage >= min_coverage:
            print(f"\n✅ Coverage meets minimum threshold ({min_coverage}%)")

            # Check critical files
            critical_files = [
                'api_main.py',
                'api_admin.py',
                'api_disc.py',
                'database.py',
                'security_scanner.py',
            ]

            print("\n📁 Critical File Coverage:")
            for package in root.findall('.//package'):
                for cls in package.findall('.//class'):
                    filename = cls.attrib.get('filename', '')
                    if any(cf in filename for cf in critical_files):
                        file_coverage = float(cls.attrib.get('line-rate', 0)) * 100
                        status = "✅" if file_coverage >= min_coverage else "⚠️"
                        print(f"  {status} {filename}: {file_coverage:.2f}%")

            return 0
        else:
            print(f"\n❌ Coverage below minimum threshold!")
            print(f"   Need {min_coverage - coverage:.2f}% more coverage")
            return 1

    except Exception as e:
        print(f"❌ Error parsing coverage file: {e}")
        return 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-coverage", type=int, default=80,
                       help="Minimum coverage percentage required")
    args = parser.parse_args()

    sys.exit(verify_coverage(args.min_coverage))
