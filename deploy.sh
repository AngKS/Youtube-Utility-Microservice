
printf "Reading environment variables...\n"

getVar() {
    VAR=$(grep $1 "./.env" | xargs)
    IFS="=" read -ra VAR <<< "$VAR"
    echo ${VAR[1]}
}

AWS_REGION=$(getVar "AWS_REGION")
AWS_PROFILE=$(getVar "AWS_PROFILE")
ECR_REPO_URI=$(getVar "ECR_REPO_URI")
IMAGE_NAME=$(getVar "IMAGE_NAME")
BUILD_PLATFORM=$(getVar "BUILD_PLATFORM")

# print the environment variables read
echo "AWS_REGION: $AWS_REGION"
echo "AWS_PROFILE: $AWS_PROFILE"
echo "ECR_REPO_URI: $ECR_REPO_URI"
echo "IMAGE_NAME: $IMAGE_NAME"
echo "BUILD_PLATFORM: $BUILD_PLATFORM"

# set the AWS profile
printf "Setting the AWS profile...\n"
export AWS_PROFILE=$AWS_PROFILE


# login to ECR
printf "Logging in to ECR...\n"

aws ecr get-login-password \
    --region $AWS_REGION \
    | docker login --username AWS --password-stdin \
    $ECR_REPO_URI

# build and push the image
printf "Building and pushing the image...\n"

docker build \
    --platform=$BUILD_PLATFORM \
    -t $IMAGE_NAME .
docker tag $IMAGE_NAME:latest $ECR_REPO_URI:latest
docker push $ECR_REPO_URI:latest  # push the correctly tagged image

# print the image URI
echo "Image Deployment successful at: $ECR_REPO_URI/$IMAGE_NAME:latest"
