import pkg_resources

# Get the list of installed packages
installed_packages = [f"{d.project_name}=={d.version}" for d in pkg_resources.working_set]

# Save to a file
file_path = "installed_packages.txt"
with open(file_path, "w") as file:
    file.write("\n".join(installed_packages))

print(f"List of installed packages saved to '{file_path}'")
